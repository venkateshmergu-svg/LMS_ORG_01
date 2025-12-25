"""Unit tests for HRIS adapter and stub."""

from datetime import datetime
from uuid import uuid4

import pytest

from lms.app.integrations.hris.adapter import HRISDepartment, HRISEmployee
from lms.app.integrations.hris.stub_adapter import StubHRISAdapter


class TestHRISDepartment:
    """Tests for HRISDepartment dataclass."""

    def test_create_department(self):
        """Should create a department with required fields."""
        dept = HRISDepartment(
            organization_code="ACME",
            department_code="ENGINEERING",
            name="Engineering",
        )

        assert dept.organization_code == "ACME"
        assert dept.department_code == "ENGINEERING"
        assert dept.name == "Engineering"
        assert dept.is_active is True  # default

    def test_department_with_inactive_status(self):
        """Should create inactive department."""
        dept = HRISDepartment(
            organization_code="ACME",
            department_code="LEGACY",
            name="Legacy Dept",
            is_active=False,
        )

        assert dept.is_active is False

    def test_department_is_frozen(self):
        """HRISDepartment should be immutable."""
        dept = HRISDepartment(
            organization_code="ACME",
            department_code="ENG",
            name="Engineering",
        )

        with pytest.raises(AttributeError):
            dept.name = "Changed"


class TestHRISEmployee:
    """Tests for HRISEmployee dataclass."""

    def test_create_employee_required_fields(self):
        """Should create employee with required fields only."""
        emp = HRISEmployee(
            organization_code="ACME",
            employee_id="EMP001",
            email="john@acme.com",
            first_name="John",
            last_name="Doe",
            department_code=None,
            manager_employee_id=None,
        )

        assert emp.organization_code == "ACME"
        assert emp.employee_id == "EMP001"
        assert emp.email == "john@acme.com"
        assert emp.first_name == "John"
        assert emp.last_name == "Doe"

    def test_create_employee_all_fields(self):
        """Should create employee with all fields."""
        hire = datetime(2020, 1, 15)

        emp = HRISEmployee(
            organization_code="ACME",
            employee_id="EMP002",
            email="jane@acme.com",
            first_name="Jane",
            last_name="Smith",
            department_code="ENGINEERING",
            manager_employee_id="EMP001",
            job_title="Senior Developer",
            employment_type="full_time",
            hire_date=hire,
            termination_date=None,
        )

        assert emp.department_code == "ENGINEERING"
        assert emp.manager_employee_id == "EMP001"
        assert emp.job_title == "Senior Developer"
        assert emp.employment_type == "full_time"
        assert emp.hire_date == hire

    def test_employee_is_frozen(self):
        """HRISEmployee should be immutable."""
        emp = HRISEmployee(
            organization_code="ACME",
            employee_id="EMP001",
            email="john@acme.com",
            first_name="John",
            last_name="Doe",
            department_code=None,
            manager_employee_id=None,
        )

        with pytest.raises(AttributeError):
            emp.email = "changed@acme.com"


class TestStubHRISAdapter:
    """Tests for StubHRISAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create a stub adapter."""
        return StubHRISAdapter()

    def test_fetch_departments_returns_list(self, adapter):
        """fetch_departments should return a list."""
        result = adapter.fetch_departments()

        assert isinstance(result, list)

    def test_fetch_departments_returns_hris_departments(self, adapter):
        """fetch_departments should return HRISDepartment instances."""
        result = adapter.fetch_departments()

        for dept in result:
            assert isinstance(dept, HRISDepartment)

    def test_fetch_employees_returns_list(self, adapter):
        """fetch_employees should return a list."""
        result = adapter.fetch_employees()

        assert isinstance(result, list)

    def test_fetch_employees_returns_hris_employees(self, adapter):
        """fetch_employees should return HRISEmployee instances."""
        result = adapter.fetch_employees()

        for emp in result:
            assert isinstance(emp, HRISEmployee)
