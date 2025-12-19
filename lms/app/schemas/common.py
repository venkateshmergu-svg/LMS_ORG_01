"""Shared Pydantic schema utilities."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IdResponse(APIModel):
    id: UUID


class TimestampMixin:
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Pagination(APIModel):
    limit: int = 100
    offset: int = 0


class MessageResponse(APIModel):
    message: str
    extra: Optional[dict[str, Any]] = None
