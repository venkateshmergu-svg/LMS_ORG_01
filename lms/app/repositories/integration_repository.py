"""Integration repositories.

Auxiliary persistence for integration tracking (idempotency, exports).
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.integration import PayrollExportRecord
from .audit_context import AuditContext
from .base import BaseRepository


class PayrollExportRepository(BaseRepository[PayrollExportRecord]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, PayrollExportRecord, audit_repo=audit_repo)

    def get_by_key(self, export_key: str) -> Optional[PayrollExportRecord]:
        stmt = select(PayrollExportRecord).where(
            PayrollExportRecord.export_key == export_key
        )
        return self.session.execute(stmt).scalars().first()

    def mark_sent(
        self,
        *,
        leave_request_id,
        employee_id: str,
        leave_type_code: str,
        start_date: date,
        end_date: date,
        adapter_name: str,
        export_key: str,
        exported_at,
        ctx: AuditContext,
    ) -> PayrollExportRecord:
        existing = self.get_by_key(export_key)
        if existing:
            return existing
        record = PayrollExportRecord(
            leave_request_id=leave_request_id,
            employee_id=employee_id,
            leave_type_code=leave_type_code,
            start_date=start_date,
            end_date=end_date,
            adapter_name=adapter_name,
            export_key=export_key,
            status="SENT",
            exported_at=exported_at,
        )
        return self.add(record, ctx=ctx, description="Payroll export: mark SENT")
