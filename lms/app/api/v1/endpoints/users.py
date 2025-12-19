"""User endpoints (minimal)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from ....engines import UserEngine
from ....models.user import User
from ....repositories import AuditContext
from ....schemas.user import CreateUserRequest, UserResponse
from ...deps import get_audit_context, get_user_engine

router = APIRouter()


@router.post("", response_model=UserResponse)
def create_user(
    payload: CreateUserRequest,
    engine: UserEngine = Depends(get_user_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    user = User(
        employee_id=payload.employee_id,
        email=str(payload.email),
        first_name=payload.first_name,
        last_name=payload.last_name,
        organization_id=payload.organization_id,
        department_id=payload.department_id,
        manager_id=payload.manager_id,
        job_title=payload.job_title,
        employment_type=payload.employment_type,
        hire_date=payload.hire_date,
        probation_end_date=payload.probation_end_date,
    )
    created = engine.create_user(user=user, ctx=ctx)
    return created.user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, engine: UserEngine = Depends(get_user_engine)):
    return engine.get_user(user_id=user_id)
