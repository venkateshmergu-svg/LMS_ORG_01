"""Leave domain repositories."""

from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from ..models.leave import (
    AccrualSchedule,
    BalanceTransaction,
    LeaveBalance,
    LeavePolicy,
    LeaveType,
    PolicyAssignment,
)
from ..models.workflow import LeaveRequest, LeaveRequestComment, LeaveRequestDate
from .base import BaseRepository


class LeaveTypeRepository(BaseRepository[LeaveType]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, LeaveType, audit_repo=audit_repo)

    def get_by_code(self, organization_id: UUID, code: str) -> Optional[LeaveType]:
        stmt = select(LeaveType).where(LeaveType.organization_id == organization_id, LeaveType.code == code)
        return self.session.execute(stmt).scalars().first()


class LeavePolicyRepository(BaseRepository[LeavePolicy]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, LeavePolicy, audit_repo=audit_repo)

    def get_active_for_leave_type(self, organization_id: UUID, leave_type_id: UUID) -> list[LeavePolicy]:
        stmt = (
            select(LeavePolicy)
            .where(LeavePolicy.organization_id == organization_id)
            .where(LeavePolicy.leave_type_id == leave_type_id)
            .where(LeavePolicy.is_active.is_(True))
            .order_by(LeavePolicy.effective_from.desc())
        )
        return list(self.session.execute(stmt).scalars().all())


class PolicyAssignmentRepository(BaseRepository[PolicyAssignment]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, PolicyAssignment, audit_repo=audit_repo)


class LeaveBalanceRepository(BaseRepository[LeaveBalance]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, LeaveBalance, audit_repo=audit_repo)

    def get_current_balance(self, user_id: UUID, leave_type_id: UUID, on_date: date) -> Optional[LeaveBalance]:
        stmt = (
            select(LeaveBalance)
            .where(LeaveBalance.user_id == user_id)
            .where(LeaveBalance.leave_type_id == leave_type_id)
            .where(LeaveBalance.period_start <= on_date)
            .where(LeaveBalance.period_end >= on_date)
        )
        return self.session.execute(stmt).scalars().first()


class LeaveRequestRepository(BaseRepository[LeaveRequest]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, LeaveRequest, audit_repo=audit_repo)

    def find_overlaps(self, user_id: UUID, start: date, end: date) -> list[LeaveRequest]:
        stmt = (
            select(LeaveRequest)
            .where(LeaveRequest.user_id == user_id)
            .where(
                or_(
                    and_(LeaveRequest.start_date <= start, LeaveRequest.end_date >= start),
                    and_(LeaveRequest.start_date <= end, LeaveRequest.end_date >= end),
                    and_(LeaveRequest.start_date >= start, LeaveRequest.end_date <= end),
                )
            )
        )
        return list(self.session.execute(stmt).scalars().all())


class LeaveRequestDateRepository(BaseRepository[LeaveRequestDate]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, LeaveRequestDate, audit_repo=audit_repo)


class LeaveRequestCommentRepository(BaseRepository[LeaveRequestComment]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, LeaveRequestComment, audit_repo=audit_repo)


class BalanceTransactionRepository(BaseRepository[BalanceTransaction]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, BalanceTransaction, audit_repo=audit_repo)


class AccrualScheduleRepository(BaseRepository[AccrualSchedule]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, AccrualSchedule, audit_repo=audit_repo)
