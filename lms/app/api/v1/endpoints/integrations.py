"""Integration endpoints (admin-triggered).

RBAC is enforced at API layer.
Integrations use repositories and UnitOfWork-managed sessions.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends

from ....core.database import get_uow
from ....core.enums import UserRole
from ....core.rbac import require_roles
from ....core.unit_of_work import UnitOfWork
from ....integrations.calendar.service import CalendarIntegrationService
from ....integrations.hris.stub_adapter import StubHRISAdapter
from ....integrations.hris.sync_service import HRISSyncService
from ....integrations.payroll.export_service import PayrollExportService
from ....integrations.payroll.stub_adapter import StubPayrollAdapter
from ....repositories import AuditContext
from ....schemas.integrations import (
    CalendarEventsResponse,
    PayrollExportRequest,
    PayrollExportResponse,
    SyncHRISResponse,
)
from ...deps import get_audit_context

router = APIRouter()


@router.post(
    "/hris/sync",
    response_model=SyncHRISResponse,
    dependencies=[Depends(require_roles(UserRole.SYSTEM_ADMIN))],
)
def sync_hris(
    uow: UnitOfWork = Depends(get_uow), ctx: AuditContext = Depends(get_audit_context)
):
    service = HRISSyncService(uow.session)
    adapter = StubHRISAdapter()
    summary = service.sync(adapter, ctx)
    return SyncHRISResponse(**summary)


@router.post(
    "/payroll/export",
    response_model=PayrollExportResponse,
    dependencies=[Depends(require_roles(UserRole.HR_ADMIN))],
)
def export_payroll(
    payload: PayrollExportRequest,
    uow: UnitOfWork = Depends(get_uow),
    ctx: AuditContext = Depends(get_audit_context),
):
    service = PayrollExportService(uow.session)
    adapter = StubPayrollAdapter()
    result = service.export(
        adapter, start_date=payload.start_date, end_date=payload.end_date, ctx=ctx
    )
    return PayrollExportResponse(**result)


@router.get(
    "/calendar/events",
    response_model=CalendarEventsResponse,
    dependencies=[Depends(require_roles(UserRole.HR_ADMIN))],
)
def calendar_events(
    start_date: date, end_date: date, uow: UnitOfWork = Depends(get_uow)
):
    service = CalendarIntegrationService(uow.session)
    events = service.generate_events(start_date, end_date)
    return CalendarEventsResponse(events=events)
