"""User-related schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from ..core.enums import UserStatus
from .common import APIModel, TimestampMixin


class UserResponse(APIModel, TimestampMixin):
    id: UUID
    employee_id: str
    email: EmailStr
    first_name: str
    last_name: str
    organization_id: UUID
    department_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    status: UserStatus


class CreateUserRequest(BaseModel):
    employee_id: str
    email: EmailStr
    first_name: str
    last_name: str
    organization_id: UUID
    department_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None

    job_title: Optional[str] = None
    employment_type: Optional[str] = None
    hire_date: Optional[datetime] = None
    probation_end_date: Optional[datetime] = None
