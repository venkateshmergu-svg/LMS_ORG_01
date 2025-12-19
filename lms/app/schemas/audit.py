"""Audit schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from ..core.enums import AuditAction
from .common import APIModel


class AuditLogResponse(APIModel):
    id: UUID
    timestamp: datetime

    actor_id: Optional[UUID] = None
    actor_type: str
    actor_ip: Optional[str] = None
    actor_user_agent: Optional[str] = None

    action: AuditAction

    entity_type: str
    entity_id: UUID

    organization_id: Optional[UUID] = None

    old_values: Optional[dict[str, Any]] = None
    new_values: Optional[dict[str, Any]] = None
    changes: Optional[dict[str, Any]] = None

    description: Optional[str] = None
    extra_metadata: Optional[dict[str, Any]] = None

    request_id: Optional[str] = None
    session_id: Optional[str] = None
