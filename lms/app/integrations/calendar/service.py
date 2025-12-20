"""Calendar integration (thin, read-only).

Transforms approved leave requests into calendar-friendly event objects.
No write-back; intended for external consumption.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from ...repositories import AuditRepository, LeaveRequestRepository, UserRepository


class CalendarIntegrationService:
    def __init__(self, session: Session):
        self.session = session
        self.audit_repo = AuditRepository(session)
        self.request_repo = LeaveRequestRepository(session, audit_repo=self.audit_repo)
        self.user_repo = UserRepository(session, audit_repo=self.audit_repo)

    def generate_events(self, start_date: date, end_date: date) -> list[dict[str, Any]]:
        approved = self.request_repo.list_approved_between(start_date, end_date)
        events: list[dict[str, Any]] = []
        for req in approved:
            from uuid import UUID

            user_id = (
                req.user_id if isinstance(req.user_id, UUID) else UUID(str(req.user_id))
            )
            user = self.user_repo.get_required(user_id)
            events.append(
                {
                    "title": f"{user.full_name} on {req.leave_type.code if req.leave_type else 'Leave'}",
                    "user_employee_id": user.employee_id,
                    "user_id": str(user.id),
                    "start_date": req.start_date.isoformat(),
                    "end_date": req.end_date.isoformat(),
                    "days": float(req.total_days),
                    "leave_request_id": str(req.id),
                }
            )
        return events
