"""Payroll export service (outbound).

Builds export rows from approved leave requests and calls a payroll adapter.
Marks successful exports as SENT with an idempotency key to prevent duplicates.

Safety:
- Read-only of domain data; does not change leave state or balances
- Uses integration repository for tracking
- Emits audit logs via repositories

Performance optimizations:
- Uses eager-loaded relationships from repository (no N+1 queries)
- Batch processes transactions efficiently
"""

from __future__ import annotations

from datetime import date
from typing import Iterable
from uuid import UUID

from sqlalchemy.orm import Session

from ...models.workflow import LeaveRequest
from ...repositories import (
    AuditContext,
    AuditRepository,
    LeaveRequestRepository,
    PayrollExportRepository,
    UserRepository,
)
from .adapter import PayrollAdapter, PayrollTransaction


class PayrollExportService:
    def __init__(self, session: Session):
        self.session = session
        self.audit_repo = AuditRepository(session)
        self.request_repo = LeaveRequestRepository(session, audit_repo=self.audit_repo)
        self.user_repo = UserRepository(session, audit_repo=self.audit_repo)
        self.export_repo = PayrollExportRepository(session, audit_repo=self.audit_repo)

    def _to_transactions(
        self, requests: Iterable[LeaveRequest]
    ) -> list[PayrollTransaction]:
        """Convert leave requests to payroll transactions.
        
        Performance: Uses eager-loaded user relationship to avoid N+1 queries.
        """
        from datetime import date
        from typing import cast
        from uuid import UUID

        txs: list[PayrollTransaction] = []
        for req in requests:
            # Use eager-loaded relationship instead of separate query
            user = req.user
            if user is None:
                # Fallback only if relationship wasn't loaded (shouldn't happen)
                user_id = (
                    req.user_id if isinstance(req.user_id, UUID) else UUID(str(req.user_id))
                )
                user = self.user_repo.get_required(user_id)
            
            leave_type_code = (
                req.leave_type.code if req.leave_type is not None else "UNKNOWN"
            )
            emp_id = (
                user.employee_id
                if isinstance(user.employee_id, str)
                else str(user.employee_id)
            )
            # Extract date values safely from ORM model
            start_date_value = cast(date, req.start_date)
            end_date_value = cast(date, req.end_date)
            if not isinstance(start_date_value, date):
                start_date_value = date.fromisoformat(str(start_date_value))
            if not isinstance(end_date_value, date):
                end_date_value = date.fromisoformat(str(end_date_value))
            txs.append(
                PayrollTransaction(
                    leave_request_id=str(req.id),
                    employee_id=emp_id,
                    leave_type_code=leave_type_code,
                    days_used=float(req.total_days),
                    start_date=start_date_value,
                    end_date=end_date_value,
                )
            )
        return txs

    def export(
        self,
        adapter: PayrollAdapter,
        start_date: date,
        end_date: date,
        ctx: AuditContext,
    ) -> dict:
        approved = self.request_repo.list_approved_between(start_date, end_date)
        transactions = self._to_transactions(approved)

        if not transactions:
            return {
                "exported": 0,
                "skipped": 0,
                "message": "No approved leave in range",
            }

        result = adapter.export_leave_transactions(transactions)

        # Mark as SENT idempotently
        exported_count = 0
        for tx in transactions:
            key = f"{adapter.__class__.__name__}:{tx.leave_request_id}:{start_date.isoformat()}:{end_date.isoformat()}"
            # Mark idempotently; does not mutate leave
            rec = self.export_repo.mark_sent(
                leave_request_id=UUID(tx.leave_request_id),
                employee_id=tx.employee_id,
                leave_type_code=tx.leave_type_code,
                start_date=start_date,
                end_date=end_date,
                adapter_name=adapter.__class__.__name__,
                export_key=key,
                exported_at=result.exported_at,
                ctx=ctx,
            )
            if rec:
                exported_count += 1

        return {
            "exported": exported_count,
            "succeeded": result.succeeded,
            "message": result.message,
        }
