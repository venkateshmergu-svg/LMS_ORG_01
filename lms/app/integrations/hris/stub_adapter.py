"""Stub/mock HRIS adapter.

Returns deterministic data for testing idempotent sync flows.
No external calls.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .adapter import HRISAdapter, HRISDepartment, HRISEmployee


class StubHRISAdapter(HRISAdapter):
    def fetch_departments(self) -> list[HRISDepartment]:
        return [
            HRISDepartment(
                organization_code="ORG1",
                department_code="ENG",
                name="Engineering",
                is_active=True,
            ),
            HRISDepartment(
                organization_code="ORG1",
                department_code="HR",
                name="Human Resources",
                is_active=True,
            ),
        ]

    def fetch_employees(self) -> list[HRISEmployee]:
        return [
            HRISEmployee(
                organization_code="ORG1",
                employee_id="E1001",
                email="alice@example.com",
                first_name="Alice",
                last_name="Doe",
                department_code="ENG",
                manager_employee_id=None,
                job_title="Software Engineer",
                employment_type="full_time",
                hire_date=datetime(2024, 1, 10, tzinfo=timezone.utc),
                termination_date=None,
            ),
            HRISEmployee(
                organization_code="ORG1",
                employee_id="E1002",
                email="bob@example.com",
                first_name="Bob",
                last_name="Smith",
                department_code="HR",
                manager_employee_id="E1003",
                job_title="HR Specialist",
                employment_type="full_time",
                hire_date=datetime(2023, 6, 1, tzinfo=timezone.utc),
                termination_date=None,
            ),
            HRISEmployee(
                organization_code="ORG1",
                employee_id="E1003",
                email="carol@example.com",
                first_name="Carol",
                last_name="Jones",
                department_code="HR",
                manager_employee_id=None,
                job_title="HR Manager",
                employment_type="full_time",
                hire_date=datetime(2020, 3, 1, tzinfo=timezone.utc),
                termination_date=None,
            ),
        ]
