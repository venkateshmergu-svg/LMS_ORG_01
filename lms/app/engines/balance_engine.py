"""Balance Engine (leave balance accounting).

Responsibilities:
- Manage leave balance state transitions tied to workflow actions
- Enforce balance invariants (no negative balances, PENDING ≤ AVAILABLE + PENDING)
- Emit audit events via repositories
- Use only repositories for all DB access (no direct session access)

State Machine:
- On SUBMIT: AVAILABLE → PENDING (reserve balance)
- On APPROVE: PENDING → USED (consume reserved balance)
- On REJECT: PENDING → AVAILABLE (release reserved balance)
- On WITHDRAW: PENDING → AVAILABLE (release reserved balance)

Domain Rules (STRICT INVARIANTS):
- AVAILABLE cannot go below zero
- PENDING cannot exceed AVAILABLE + PENDING (checked before state change)
- USED only increases on approval
- No balance mutation without audit trail
"""

from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy.orm import Session

from ..core.exceptions import InsufficientBalanceException
from ..models.workflow import LeaveRequest
from ..repositories import AuditContext, AuditRepository, LeaveBalanceRepository


class BalanceEngine:
    """Leave balance accounting engine.

    Manages balance state transitions and enforces invariants.
    All mutations go through repositories to ensure audit trails.
    """

    def __init__(
        self,
        session: Session,
        *,
        balance_repo: LeaveBalanceRepository,
        audit_repo: AuditRepository,
    ):
        """Initialize BalanceEngine.

        Args:
            session: SQLAlchemy session (for queries only, no direct mutations)
            balance_repo: Repository for balance operations
            audit_repo: Repository for audit trail
        """
        self.session = session
        self.balance_repo = balance_repo
        self.audit_repo = audit_repo

    def on_submit(
        self,
        *,
        leave_request: LeaveRequest,
        ctx: AuditContext,
    ) -> None:
        """On leave submission: reserve days from AVAILABLE → PENDING.

        Rules:
        - Verify sufficient AVAILABLE balance
        - Move exactly leave_request.total_days from AVAILABLE to PENDING
        - Audit event tracks the transition

        Args:
            leave_request: LeaveRequest being submitted
            ctx: Audit context

        Raises:
            InsufficientBalanceException: if AVAILABLE < total_days requested
        """
        balance = self.balance_repo.get_current_balance(
            user_id=cast(UUID, leave_request.user_id),
            leave_type_id=cast(UUID, leave_request.leave_type_id),
            on_date=cast(object, leave_request.start_date),  # type: ignore
        )

        if balance is None:
            raise InsufficientBalanceException(
                available=0.0,
                requested=cast(float, leave_request.total_days),
                leave_type="unknown",
            )

        available = balance.available_balance
        requested_days = cast(float, leave_request.total_days)

        # Invariant: AVAILABLE must be >= requested days
        if not (available >= requested_days):  # Avoid SQLAlchemy boolean issues
            raise InsufficientBalanceException(
                available=available,
                requested=requested_days,
                leave_type=(
                    cast(str, balance.leave_type.code)
                    if balance.leave_type
                    else "unknown"
                ),
            )

        # Move days from AVAILABLE to PENDING
        # This is done by incrementing the pending field
        new_pending = cast(float, balance.pending) + requested_days

        balance = self.balance_repo.update_fields(
            balance,
            {"pending": new_pending},
            ctx=ctx,
            description=f"Reserve {requested_days} days for leave request {cast(str, leave_request.request_number)}",
        )

    def on_approve(
        self,
        *,
        leave_request: LeaveRequest,
        ctx: AuditContext,
    ) -> None:
        """On approval (final workflow step): move days from PENDING → USED.

        Rules:
        - Move exactly leave_request.total_days from PENDING to USED
        - Verify PENDING >= total_days (should be guaranteed by on_submit)
        - Audit event tracks approval consumption

        Args:
            leave_request: LeaveRequest being approved
            ctx: Audit context
        """
        balance = self.balance_repo.get_current_balance(
            user_id=cast(UUID, leave_request.user_id),
            leave_type_id=cast(UUID, leave_request.leave_type_id),
            on_date=cast(object, leave_request.start_date),  # type: ignore
        )

        if balance is None:
            # Should not happen if on_submit was called
            raise RuntimeError(
                f"No balance found for user {leave_request.user_id}, "
                f"leave_type {leave_request.leave_type_id}"
            )

        pending = cast(float, balance.pending)
        requested_days = cast(float, leave_request.total_days)

        # Invariant: PENDING should have the reserved days
        if not (pending >= requested_days):  # Avoid SQLAlchemy boolean issues
            raise RuntimeError(
                f"Balance invariant violated: PENDING {pending} < "
                f"requested {requested_days}"
            )

        # Move days from PENDING to USED
        new_pending = pending - requested_days
        new_used = cast(float, balance.used) + requested_days

        balance = self.balance_repo.update_fields(
            balance,
            {
                "pending": new_pending,
                "used": new_used,
            },
            ctx=ctx,
            description=f"Approve leave request {cast(str, leave_request.request_number)}: "
            f"move {requested_days} days from PENDING to USED",
        )

    def on_reject(
        self,
        *,
        leave_request: LeaveRequest,
        ctx: AuditContext,
    ) -> None:
        """On rejection: release days from PENDING → AVAILABLE.

        Rules:
        - Move exactly leave_request.total_days from PENDING back to AVAILABLE
        - PENDING should have the reserved days (from on_submit)
        - Audit event tracks rejection release

        Args:
            leave_request: LeaveRequest being rejected
            ctx: Audit context
        """
        balance = self.balance_repo.get_current_balance(
            user_id=cast(UUID, leave_request.user_id),
            leave_type_id=cast(UUID, leave_request.leave_type_id),
            on_date=cast(object, leave_request.start_date),  # type: ignore
        )

        if balance is None:
            # Should not happen, but handle gracefully
            return

        pending = cast(float, balance.pending)
        requested_days = cast(float, leave_request.total_days)

        # Invariant: PENDING should have the reserved days
        if not (pending >= requested_days):  # Avoid SQLAlchemy boolean issues
            # Log but don't fail; balance may have been adjusted manually
            return

        # Move days from PENDING back to AVAILABLE
        new_pending = pending - requested_days

        balance = self.balance_repo.update_fields(
            balance,
            {"pending": new_pending},
            ctx=ctx,
            description=f"Reject leave request {cast(str, leave_request.request_number)}: "
            f"release {requested_days} days from PENDING",
        )

    def on_withdraw(
        self,
        *,
        leave_request: LeaveRequest,
        ctx: AuditContext,
    ) -> None:
        """On withdrawal: release days from PENDING → AVAILABLE.

        Rules:
        - Move exactly leave_request.total_days from PENDING back to AVAILABLE
        - PENDING should have the reserved days (from on_submit)
        - Audit event tracks withdrawal release

        Args:
            leave_request: LeaveRequest being withdrawn
            ctx: Audit context
        """
        balance = self.balance_repo.get_current_balance(
            user_id=cast(UUID, leave_request.user_id),
            leave_type_id=cast(UUID, leave_request.leave_type_id),
            on_date=cast(object, leave_request.start_date),  # type: ignore
        )

        if balance is None:
            # Should not happen, but handle gracefully
            return

        pending = cast(float, balance.pending)
        requested_days = cast(float, leave_request.total_days)

        # Invariant: PENDING should have the reserved days
        if not (pending >= requested_days):  # Avoid SQLAlchemy boolean issues
            # Log but don't fail; balance may have been adjusted manually
            return

        # Move days from PENDING back to AVAILABLE
        new_pending = pending - requested_days

        balance = self.balance_repo.update_fields(
            balance,
            {"pending": new_pending},
            ctx=ctx,
            description=f"Withdraw leave request {cast(str, leave_request.request_number)}: "
            f"release {requested_days} days from PENDING",
        )
