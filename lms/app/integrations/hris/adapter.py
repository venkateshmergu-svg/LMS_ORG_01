"""HRIS adapter interfaces and data contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class HRISDepartment:
    organization_code: str
    department_code: str
    name: str
    is_active: bool = True


@dataclass(frozen=True)
class HRISEmployee:
    organization_code: str
    employee_id: str
    email: str
    first_name: str
    last_name: str
    department_code: str | None
    manager_employee_id: str | None
    job_title: str | None = None
    employment_type: str | None = None
    hire_date: datetime | None = None
    termination_date: datetime | None = None


class HRISAdapter(Protocol):
    """Port interface for external HRIS providers (inbound sync)."""

    def fetch_departments(self) -> list[HRISDepartment]:
        """Return list of departments from HRIS."""

    def fetch_employees(self) -> list[HRISEmployee]:
        """Return list of employees from HRIS."""
