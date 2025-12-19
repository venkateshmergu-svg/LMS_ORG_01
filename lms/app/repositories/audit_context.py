"""Audit context passed through repositories.

Repositories are responsible for emitting audit events for all mutations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID


@dataclass(frozen=True)
class AuditContext:
    actor_id: Optional[UUID] = None
    actor_type: str = "system"  # user|system|scheduler
    actor_ip: Optional[str] = None
    actor_user_agent: Optional[str] = None

    organization_id: Optional[UUID] = None

    request_id: Optional[str] = None
    session_id: Optional[str] = None

    extra: Optional[dict[str, Any]] = None
