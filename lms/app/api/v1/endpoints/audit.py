"""Audit endpoints (read-only)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from ....engines import AuditEngine
from ....schemas.audit import AuditLogResponse
from ...deps import get_audit_engine

router = APIRouter()


@router.get("/{entity_type}/{entity_id}", response_model=list[AuditLogResponse])
def list_audit_events(
    entity_type: str,
    entity_id: UUID,
    limit: int = 100,
    offset: int = 0,
    engine: AuditEngine = Depends(get_audit_engine),
):
    return engine.list_entity_events(entity_type=entity_type, entity_id=entity_id, limit=limit, offset=offset)
