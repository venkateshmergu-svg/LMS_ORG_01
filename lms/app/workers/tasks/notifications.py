"""Notification tasks."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ...core.database import SessionLocal
from ...repositories import AuditContext, AuditRepository, NotificationRepository
from ..celery_app import celery_app


@celery_app.task(name="lms.notifications.send_pending")
def send_pending_notifications() -> dict:
    """Send pending notifications.

    Skeleton only: fetch pending notifications and send via integration.
    """
    session: Session = SessionLocal()
    try:
        audit_repo = AuditRepository(session)
        _ctx = AuditContext(actor_id=None, actor_type="scheduler")
        _repo = NotificationRepository(session, audit_repo=audit_repo)
        # Future: pull pending, call integrations, update status through repository.
        return {"status": "ok"}
    finally:
        session.close()
