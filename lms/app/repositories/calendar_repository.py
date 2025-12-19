"""Calendar repositories."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.calendar import Holiday, HolidayCalendar
from .base import BaseRepository


class HolidayCalendarRepository(BaseRepository[HolidayCalendar]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, HolidayCalendar, audit_repo=audit_repo)

    def get_default_for_year(self, organization_id: UUID, year: int) -> Optional[HolidayCalendar]:
        stmt = select(HolidayCalendar).where(
            HolidayCalendar.organization_id == organization_id,
            HolidayCalendar.year == year,
            HolidayCalendar.is_default.is_(True),
            HolidayCalendar.is_active.is_(True),
        )
        return self.session.execute(stmt).scalars().first()


class HolidayRepository(BaseRepository[Holiday]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, Holiday, audit_repo=audit_repo)

    def list_for_calendar(self, calendar_id: UUID) -> list[Holiday]:
        stmt = select(Holiday).where(Holiday.calendar_id == calendar_id).order_by(Holiday.date.asc())
        return list(self.session.execute(stmt).scalars().all())
