"""Accrual tasks.

These tasks are intentionally thin wrappers.
They acquire a DB session and call engines/repositories.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from ...core.database import SessionLocal
from ...engines import PolicyEngine
from ...repositories import (
    AccrualScheduleRepository,
    AuditContext,
    AuditRepository,
    LeaveBalanceRepository,
    LeavePolicyRepository,
    PolicyAssignmentRepository,
)
from ..celery_app import celery_app


@celery_app.task(name="lms.accrual.run_policy_accrual")
def run_policy_accrual(policy_id: str, on_date_iso: str) -> dict:
    """Run accrual for a single policy.

    Skeleton only: loads policy and iterates eligible users later.
    """
    session: Session = SessionLocal()
    try:
        audit_repo = AuditRepository(session)
        ctx = AuditContext(actor_id=None, actor_type="scheduler")

        policy_repo = LeavePolicyRepository(session, audit_repo=audit_repo)
        assignment_repo = PolicyAssignmentRepository(session, audit_repo=audit_repo)
        balance_repo = LeaveBalanceRepository(session, audit_repo=audit_repo)
        schedule_repo = AccrualScheduleRepository(session, audit_repo=audit_repo)

        engine = PolicyEngine(
            session,
            policy_repo=policy_repo,
            assignment_repo=assignment_repo,
            balance_repo=balance_repo,
        )

        _ = engine  # placeholder to avoid unused warnings; expand in next iterations

        # Mark schedule executed etc. (future)
        return {"status": "ok", "policy_id": policy_id, "on_date": on_date_iso}
    finally:
        session.close()
