"""Audit repository (append-only).

All audit events must be inserted via this repository.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.enums import AuditAction
from ..models.audit import AuditLog
from .audit_context import AuditContext


class AuditRepository:
    def __init__(self, session: Session):
        self.session = session

    def append(
        self,
        *,
        action: AuditAction,
        entity_type: str,
        entity_id: UUID,
        ctx: AuditContext,
        old_values: Optional[dict[str, Any]] = None,
        new_values: Optional[dict[str, Any]] = None,
        changes: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> AuditLog:
        log = AuditLog(
            actor_id=ctx.actor_id,
            actor_type=ctx.actor_type,
            actor_ip=ctx.actor_ip,
            actor_user_agent=ctx.actor_user_agent,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            organization_id=ctx.organization_id,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            description=description,
            extra_metadata=extra_metadata or ctx.extra,
            request_id=ctx.request_id,
            session_id=ctx.session_id,
        )
        self.session.add(log)
        return log

    def list_for_entity(
        self,
        *,
        entity_type: str,
        entity_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.entity_type == entity_type)
            .where(AuditLog.entity_id == entity_id)
            .order_by(AuditLog.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())
