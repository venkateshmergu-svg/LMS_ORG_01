"""Notification repositories."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.notification import Notification, NotificationTemplate
from .base import BaseRepository


class NotificationTemplateRepository(BaseRepository[NotificationTemplate]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, NotificationTemplate, audit_repo=audit_repo)

    def get_by_code(self, organization_id: Optional[UUID], code: str) -> Optional[NotificationTemplate]:
        stmt = select(NotificationTemplate).where(NotificationTemplate.code == code)
        if organization_id is None:
            stmt = stmt.where(NotificationTemplate.organization_id.is_(None))
        else:
            stmt = stmt.where(NotificationTemplate.organization_id == organization_id)
        return self.session.execute(stmt).scalars().first()


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, Notification, audit_repo=audit_repo)

    def list_for_user(self, user_id: UUID, *, limit: int = 50, offset: int = 0) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())
