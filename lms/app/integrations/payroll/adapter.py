"""Payroll adapter interface and data contracts (outbound)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol


@dataclass(frozen=True)
class PayrollTransaction:
    leave_request_id: str
    employee_id: str
    leave_type_code: str
    days_used: float
    start_date: date
    end_date: date


@dataclass(frozen=True)
class PayrollExportResult:
    exported_count: int
    succeeded: bool
    message: str | None = None
    exported_at: datetime | None = None


class PayrollAdapter(Protocol):
    """Port interface for outbound payroll export."""

    def export_leave_transactions(
        self, transactions: list[PayrollTransaction]
    ) -> PayrollExportResult:
        """Export approved leave transactions."""
