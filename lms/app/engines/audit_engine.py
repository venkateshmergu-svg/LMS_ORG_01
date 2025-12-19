"""Audit engine.

Append-only audit is the source of truth for all state changes.
Engines should use repositories for mutations; repositories emit audit events.
This engine provides convenience read APIs and contextual helpers.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..repositories import AuditContext, AuditRepository


class AuditEngine:
    def __init__(self, session: Session):
        self.session = session
        self.audit_repo = AuditRepository(session)

    def list_entity_events(
        self,
        *,
        entity_type: str,
        entity_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ):
        return self.audit_repo.list_for_entity(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
            offset=offset,
        )

    def make_context(
        self,
        *,
        actor_id: Optional[UUID],
        actor_type: str,
        organization_id: Optional[UUID] = None,
        actor_ip: Optional[str] = None,
        actor_user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        extra: Optional[dict[str, Any]] = None,
    ) -> AuditContext:
        return AuditContext(
            actor_id=actor_id,
            actor_type=actor_type,
            actor_ip=actor_ip,
            actor_user_agent=actor_user_agent,
            organization_id=organization_id,
            request_id=request_id,
            session_id=session_id,
            extra=extra,
        )
