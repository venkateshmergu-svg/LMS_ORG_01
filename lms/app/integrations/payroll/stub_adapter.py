"""Stub payroll adapter.

Simulates exporting transactions and always succeeds.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .adapter import PayrollAdapter, PayrollExportResult, PayrollTransaction


class StubPayrollAdapter(PayrollAdapter):
    def export_leave_transactions(
        self, transactions: list[PayrollTransaction]
    ) -> PayrollExportResult:
        return PayrollExportResult(
            exported_count=len(transactions),
            succeeded=True,
            message="Stub export completed",
            exported_at=datetime.now(timezone.utc),
        )
