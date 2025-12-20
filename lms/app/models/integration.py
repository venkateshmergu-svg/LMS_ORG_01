"""Integration models (auxiliary, non-domain).

Used for tracking outbound export idempotency etc.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Column, Date, DateTime, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from ..core.database import Base
from .base import BaseModel


class PayrollExportRecord(BaseModel):
    """Tracks payroll export operations for idempotency and auditing."""

    __tablename__ = "payroll_export_records"

    # What was exported
    leave_request_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(String(50), nullable=False, index=True)
    leave_type_code = Column(String(50), nullable=False)

    # Export window
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # Adapter implementation name and idempotency key
    adapter_name = Column(String(100), nullable=False)
    export_key = Column(String(255), nullable=False, unique=True, index=True)

    # Status
    status = Column(String(20), nullable=False, default="SENT")
    exported_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "leave_request_id",
            "start_date",
            "end_date",
            "adapter_name",
            name="uq_payroll_export_window",
        ),
    )
