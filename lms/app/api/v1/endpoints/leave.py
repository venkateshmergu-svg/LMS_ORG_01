"""Compatibility Leave endpoints.

The frontend expects routes under /api/v1/leave/*.
The core domain endpoints live under /api/v1/leave-requests.

These endpoints provide a thin translation layer so the app works end-to-end.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ....core.security import AuthenticatedUser, get_authenticated_user
from ....engines import LeaveEngine
from ....repositories import AuditContext
from ...deps import get_audit_context, get_leave_engine

router = APIRouter()


class LeaveRequestCreateFrontend(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveRequestFrontend(BaseModel):
    id: str
    user_id: str
    leave_type: str
    start_date: str
    end_date: str
    days_requested: float
    reason: str
    status: str
    created_at: str
    updated_at: str


class PaginatedResponse(BaseModel):
    items: list[LeaveRequestFrontend]
    total: int
    skip: int
    limit: int


class LeaveBalanceFrontend(BaseModel):
    employee_id: str
    leave_type: str
    total_balance: float
    used: float
    pending: float
    available: float


def _map_status(value: object) -> str:
    raw = str(value)
    raw_lc = raw.lower()
    mapping = {
        "approved": "APPROVED",
        "rejected": "REJECTED",
        "withdrawn": "WITHDRAWN",
        "cancelled": "WITHDRAWN",
    }
    # draft, pending_approval, etc.
    return mapping.get(raw_lc, "PENDING")


def _to_frontend_request(req) -> LeaveRequestFrontend:
    leave_type_name = getattr(getattr(req, "leave_type", None), "name", None)
    leave_type_code = getattr(getattr(req, "leave_type", None), "code", None)
    leave_type = (
        leave_type_name or leave_type_code or str(getattr(req, "leave_type_id", ""))
    )

    start = getattr(req, "start_date")
    end = getattr(req, "end_date")

    created_at = getattr(req, "created_at", None)
    updated_at = getattr(req, "updated_at", None)

    return LeaveRequestFrontend(
        id=str(req.id),
        user_id=str(req.user_id),
        leave_type=str(leave_type),
        start_date=str(start),
        end_date=str(end),
        days_requested=float(getattr(req, "total_days", 0.0)),
        reason=str(getattr(req, "reason", "") or ""),
        status=_map_status(getattr(req, "status", "")),
        created_at=(
            str(created_at) if created_at else datetime.now(timezone.utc).isoformat()
        ),
        updated_at=(
            str(updated_at) if updated_at else datetime.now(timezone.utc).isoformat()
        ),
    )


@router.get("/requests", response_model=PaginatedResponse)
def list_my_requests(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    engine: LeaveEngine = Depends(get_leave_engine),
    auth_user: AuthenticatedUser = Depends(get_authenticated_user),
):
    # Get total count for proper pagination
    total_count = engine.count_leave_requests(user_id=auth_user.user_id, status=status)

    # Get paginated items
    items = engine.list_leave_requests(
        user_id=auth_user.user_id, status=status, limit=limit, offset=skip
    )
    return PaginatedResponse(
        items=[_to_frontend_request(r) for r in items],
        total=total_count,  # Actual total count, not page size
        skip=skip,
        limit=limit,
    )


@router.get("/requests/{request_id}", response_model=LeaveRequestFrontend)
def get_request(
    request_id: UUID,
    engine: LeaveEngine = Depends(get_leave_engine),
    auth_user: AuthenticatedUser = Depends(get_authenticated_user),
):
    req = engine.get_leave_request(request_id)
    if str(req.user_id) != str(auth_user.user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return _to_frontend_request(req)


@router.delete("/requests/{request_id}", response_model=dict)
def delete_request(
    request_id: UUID,
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
    auth_user: AuthenticatedUser = Depends(get_authenticated_user),
):
    # Frontend uses DELETE as a "withdraw" action.
    result = engine.withdraw_request(
        leave_request_id=request_id,
        actor_user_id=auth_user.user_id,
        reason=None,
        ctx=ctx,
    )
    return {
        "leave_request_id": str(result["leave_request"].id),
        "status": str(result["status"]),
    }


@router.post("/requests", response_model=LeaveRequestFrontend)
def create_request(
    payload: LeaveRequestCreateFrontend,
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
    auth_user: AuthenticatedUser = Depends(get_authenticated_user),
):
    org_id = auth_user.organization_id
    if org_id is None:
        raise HTTPException(status_code=400, detail="Missing organization context")

    code = payload.leave_type.strip().upper()
    leave_type = engine.leave_type_repo.get_by_code(org_id, code)
    if leave_type is None:
        raise HTTPException(
            status_code=400, detail=f"Unknown leave type: {payload.leave_type}"
        )

    if payload.end_date < payload.start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")

    total_days = float((payload.end_date - payload.start_date).days + 1)

    result = engine.create_leave_request(
        user_id=auth_user.user_id,
        leave_type_id=cast(UUID, leave_type.id),
        start_date=payload.start_date,
        end_date=payload.end_date,
        total_days=total_days,
        reason=payload.reason,
        ctx=ctx,
    )

    return _to_frontend_request(result.leave_request)


@router.get("/balance", response_model=LeaveBalanceFrontend)
def get_balance(
    engine: LeaveEngine = Depends(get_leave_engine),
    auth_user: AuthenticatedUser = Depends(get_authenticated_user),
):
    user = engine.user_repo.get_required(auth_user.user_id)
    summary = engine.get_leave_balance(auth_user.user_id)

    total_balance = 0.0
    used = 0.0
    pending = 0.0
    available = 0.0

    for b in summary.get("balances", []):
        opening = float(b.get("opening_balance", 0.0))
        accrued = float(b.get("accrued", 0.0))
        carried = float(b.get("carried_forward", 0.0))
        adjusted = float(b.get("adjusted", 0.0))
        total_balance += opening + accrued + carried + adjusted
        used += float(b.get("used", 0.0))
        pending += float(b.get("pending", 0.0))
        available += float(b.get("available", 0.0))

    return LeaveBalanceFrontend(
        employee_id=str(getattr(user, "employee_id", "")),
        leave_type="TOTAL",
        total_balance=total_balance,
        used=used,
        pending=pending,
        available=available,
    )
