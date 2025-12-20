"""Schemas for integration API endpoints."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from pydantic import BaseModel

from .common import APIModel


class SyncHRISResponse(APIModel):
    departments_created: int
    departments_updated: int
    users_created: int
    users_updated: int
    skipped_organizations: list[str]


class PayrollExportRequest(BaseModel):
    start_date: date
    end_date: date


class PayrollExportResponse(APIModel):
    exported: int
    succeeded: bool
    message: Optional[str] = None


class CalendarEventsResponse(APIModel):
    events: list[dict[str, Any]]
