"""Approval endpoints for managers.

Provides endpoints to list and act on pending approvals.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, selectinload

from ....core.database import get_db
from ....core.enums import LeaveRequestStatus, UserRole, WorkflowStepStatus
from ....core.rbac import RBACContext, require_roles
from ....core.security import AuthenticatedUser, get_authenticated_user
from ....models.user import User
from ....models.workflow import LeaveRequest, WorkflowStep

router = APIRouter()


class PendingApprovalItem(BaseModel):
    """A pending approval item for display in the approval queue."""

    id: str  # step_id
    step_id: str
    leave_request_id: str
    # Employee info
    employee_id: str
    employee_name: str
    # Leave details
    leave_type: str
    start_date: str
    end_date: str
    days_requested: float
    reason: Optional[str]
    # Workflow info
    status: str
    sequence: int
    submitted_at: Optional[str]
    created_at: str


class PaginatedApprovals(BaseModel):
    """Paginated response for approval queue."""

    items: list[PendingApprovalItem]
    total: int
    skip: int
    limit: int


@router.get("/pending", response_model=PaginatedApprovals)
def list_pending_approvals(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    auth_user: AuthenticatedUser = Depends(get_authenticated_user),
    rbac: RBACContext = Depends(
        require_roles(UserRole.MANAGER, UserRole.HR_ADMIN, UserRole.SYSTEM_ADMIN)
    ),
):
    """List pending approval steps for the authenticated user.

    Returns workflow steps where:
    - approver_id matches the authenticated user
    - status is PENDING
    - leave request status is PENDING_APPROVAL

    Ordered by submitted_at (oldest first - FIFO).
    """
    # Query for pending steps assigned to this approver
    stmt = (
        select(WorkflowStep)
        .join(LeaveRequest, WorkflowStep.leave_request_id == LeaveRequest.id)
        .options(
            selectinload(WorkflowStep.leave_request).selectinload(LeaveRequest.user),
            selectinload(WorkflowStep.leave_request).selectinload(
                LeaveRequest.leave_type
            ),
        )
        .where(
            and_(
                WorkflowStep.approver_id == auth_user.user_id,
                WorkflowStep.status == WorkflowStepStatus.PENDING,
                LeaveRequest.status == LeaveRequestStatus.PENDING_APPROVAL,
            )
        )
        .order_by(LeaveRequest.submitted_at.asc())
    )

    # Get total count
    from sqlalchemy import func

    count_stmt = (
        select(func.count())
        .select_from(WorkflowStep)
        .join(LeaveRequest, WorkflowStep.leave_request_id == LeaveRequest.id)
        .where(
            and_(
                WorkflowStep.approver_id == auth_user.user_id,
                WorkflowStep.status == WorkflowStepStatus.PENDING,
                LeaveRequest.status == LeaveRequestStatus.PENDING_APPROVAL,
            )
        )
    )
    total = db.execute(count_stmt).scalar() or 0

    # Get paginated results
    steps = db.execute(stmt.offset(skip).limit(limit)).scalars().all()

    items: list[PendingApprovalItem] = []
    for step in steps:
        leave_request: LeaveRequest = step.leave_request
        user: User = leave_request.user
        leave_type = leave_request.leave_type

        # Access model attributes - SQLAlchemy ORM objects have Python values
        # Type ignores needed because Pylance incorrectly infers Column types
        total_days_val: float = leave_request.total_days  # type: ignore[assignment]
        reason_val: Optional[str] = leave_request.reason  # type: ignore[assignment]
        step_order_val: int = step.step_order  # type: ignore[assignment]
        submitted_at_val = leave_request.submitted_at
        created_at_val = step.created_at

        items.append(
            PendingApprovalItem(
                id=str(step.id),
                step_id=str(step.id),
                leave_request_id=str(leave_request.id),
                employee_id=str(user.id),
                employee_name=user.full_name,
                leave_type=(
                    leave_type.name if leave_type else str(leave_request.leave_type_id)
                ),
                start_date=str(leave_request.start_date),
                end_date=str(leave_request.end_date),
                days_requested=total_days_val or 0.0,
                reason=reason_val,
                status="PENDING",
                sequence=step_order_val or 0,
                submitted_at=(
                    submitted_at_val.isoformat()  # type: ignore[union-attr]
                    if submitted_at_val is not None
                    else None
                ),
                created_at=(
                    created_at_val.isoformat()  # type: ignore[union-attr]
                    if created_at_val is not None
                    else datetime.now(timezone.utc).isoformat()
                ),
            )
        )

    return PaginatedApprovals(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{step_id}", response_model=PendingApprovalItem)
def get_approval_detail(
    step_id: UUID,
    db: Session = Depends(get_db),
    auth_user: AuthenticatedUser = Depends(get_authenticated_user),
    rbac: RBACContext = Depends(
        require_roles(UserRole.MANAGER, UserRole.HR_ADMIN, UserRole.SYSTEM_ADMIN)
    ),
):
    """Get details of a specific approval step."""
    from fastapi import HTTPException

    stmt = (
        select(WorkflowStep)
        .options(
            selectinload(WorkflowStep.leave_request).selectinload(LeaveRequest.user),
            selectinload(WorkflowStep.leave_request).selectinload(
                LeaveRequest.leave_type
            ),
        )
        .where(WorkflowStep.id == step_id)
    )

    step = db.execute(stmt).scalars().first()
    if not step:
        raise HTTPException(status_code=404, detail="Approval step not found")

    # Verify the user is the assigned approver (or admin)
    approver_id_val: UUID = step.approver_id  # type: ignore[assignment]
    if approver_id_val != auth_user.user_id and not rbac.is_system_admin():
        raise HTTPException(
            status_code=403, detail="Not authorized to view this approval"
        )

    leave_request: LeaveRequest = step.leave_request
    user: User = leave_request.user
    leave_type = leave_request.leave_type

    # Access model attributes - SQLAlchemy ORM objects have Python values
    # Type ignores needed because Pylance incorrectly infers Column types
    total_days_val: float = leave_request.total_days  # type: ignore[assignment]
    reason_val: Optional[str] = leave_request.reason  # type: ignore[assignment]
    step_order_val: int = step.step_order  # type: ignore[assignment]
    submitted_at_val = leave_request.submitted_at
    created_at_val = step.created_at

    return PendingApprovalItem(
        id=str(step.id),
        step_id=str(step.id),
        leave_request_id=str(leave_request.id),
        employee_id=str(user.id),
        employee_name=user.full_name,
        leave_type=leave_type.name if leave_type else str(leave_request.leave_type_id),
        start_date=str(leave_request.start_date),
        end_date=str(leave_request.end_date),
        days_requested=total_days_val or 0.0,
        reason=reason_val,
        status=step.status.value.upper(),
        sequence=step_order_val or 0,
        submitted_at=(
            submitted_at_val.isoformat()  # type: ignore[union-attr]
            if submitted_at_val is not None
            else None
        ),
        created_at=(
            created_at_val.isoformat()  # type: ignore[union-attr]
            if created_at_val is not None
            else datetime.now(timezone.utc).isoformat()
        ),
    )
