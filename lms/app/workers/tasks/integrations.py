"""Integration task placeholders.

Thin wrappers to trigger HRIS sync and Payroll export in background.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from ...core.database import SessionLocal
from ...integrations.hris.stub_adapter import StubHRISAdapter
from ...integrations.hris.sync_service import HRISSyncService
from ...integrations.payroll.export_service import PayrollExportService
from ...integrations.payroll.stub_adapter import StubPayrollAdapter
from ...repositories import AuditContext, AuditRepository
from ..celery_app import celery_app


@celery_app.task(name="lms.integrations.sync_hris")
def sync_hris_task() -> dict:
    session: Session = SessionLocal()
    try:
        audit_repo = AuditRepository(session)
        ctx = AuditContext(actor_id=None, actor_type="scheduler")
        service = HRISSyncService(session)
        adapter = StubHRISAdapter()
        return service.sync(adapter, ctx)
    finally:
        session.close()


@celery_app.task(name="lms.integrations.export_payroll")
def export_payroll_task(start_date_iso: str, end_date_iso: str) -> dict:
    session: Session = SessionLocal()
    try:
        audit_repo = AuditRepository(session)
        ctx = AuditContext(actor_id=None, actor_type="scheduler")
        service = PayrollExportService(session)
        adapter = StubPayrollAdapter()
        start = date.fromisoformat(start_date_iso)
        end = date.fromisoformat(end_date_iso)
        return service.export(adapter, start_date=start, end_date=end, ctx=ctx)
    finally:
        session.close()
