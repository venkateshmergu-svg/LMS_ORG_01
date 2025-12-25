"""Unit tests for HRIS sync service."""

from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.core.enums import UserStatus
from lms.app.integrations.hris.adapter import HRISDepartment, HRISEmployee


class TestHRISSyncService:
    """Tests for HRISSyncService."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock SQLAlchemy session."""
        return MagicMock()

    @pytest.fixture
    def audit_ctx(self):
        """Create a mock audit context."""
        ctx = MagicMock()
        ctx.actor_id = None
        ctx.actor_type = "scheduler"
        return ctx

    @pytest.fixture
    def mock_org(self):
        """Create a mock organization."""
        org = MagicMock()
        org.id = uuid4()
        org.code = "ORG1"
        return org

    @pytest.fixture
    def mock_department(self):
        """Create a mock department."""
        dept = MagicMock()
        dept.id = uuid4()
        dept.code = "ENG"
        dept.name = "Engineering"
        dept.is_active = True
        return dept

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = MagicMock()
        user.id = uuid4()
        user.employee_id = "EMP001"
        user.email = "user@example.com"
        user.first_name = "John"
        user.last_name = "Doe"
        user.department_id = None
        user.manager_id = None
        user.job_title = "Developer"
        user.employment_type = "full_time"
        user.hire_date = None
        user.termination_date = None
        user.status = UserStatus.ACTIVE
        return user

    @patch("lms.app.integrations.hris.sync_service.AuditRepository")
    @patch("lms.app.integrations.hris.sync_service.OrganizationRepository")
    @patch("lms.app.integrations.hris.sync_service.DepartmentRepository")
    @patch("lms.app.integrations.hris.sync_service.UserRepository")
    def test_sync_with_empty_adapter(
        self,
        mock_user_repo_cls,
        mock_dept_repo_cls,
        mock_org_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        audit_ctx,
    ):
        """sync should handle empty adapter data."""
        mock_adapter = MagicMock()
        mock_adapter.fetch_departments.return_value = []
        mock_adapter.fetch_employees.return_value = []

        from lms.app.integrations.hris.sync_service import HRISSyncService

        service = HRISSyncService(mock_session)
        result = service.sync(mock_adapter, audit_ctx)

        assert result["departments_created"] == 0
        assert result["users_created"] == 0

    @patch("lms.app.integrations.hris.sync_service.AuditRepository")
    @patch("lms.app.integrations.hris.sync_service.OrganizationRepository")
    @patch("lms.app.integrations.hris.sync_service.DepartmentRepository")
    @patch("lms.app.integrations.hris.sync_service.UserRepository")
    def test_sync_skips_unknown_org(
        self,
        mock_user_repo_cls,
        mock_dept_repo_cls,
        mock_org_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        audit_ctx,
    ):
        """sync should skip items with unknown organization."""
        mock_org_repo = MagicMock()
        mock_org_repo.get_by_code.return_value = None  # Org not found
        mock_org_repo_cls.return_value = mock_org_repo

        mock_adapter = MagicMock()
        mock_adapter.fetch_departments.return_value = [
            HRISDepartment(
                organization_code="UNKNOWN",
                department_code="ENG",
                name="Engineering",
            )
        ]
        mock_adapter.fetch_employees.return_value = []

        from lms.app.integrations.hris.sync_service import HRISSyncService

        service = HRISSyncService(mock_session)
        result = service.sync(mock_adapter, audit_ctx)

        assert "UNKNOWN" in result["skipped_organizations"]

    @patch("lms.app.integrations.hris.sync_service.AuditRepository")
    @patch("lms.app.integrations.hris.sync_service.OrganizationRepository")
    @patch("lms.app.integrations.hris.sync_service.DepartmentRepository")
    @patch("lms.app.integrations.hris.sync_service.UserRepository")
    def test_sync_creates_new_department(
        self,
        mock_user_repo_cls,
        mock_dept_repo_cls,
        mock_org_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_org,
        audit_ctx,
    ):
        """sync should create new departments."""
        mock_org_repo = MagicMock()
        mock_org_repo.get_by_code.return_value = mock_org
        mock_org_repo_cls.return_value = mock_org_repo

        mock_dept_repo = MagicMock()
        mock_dept_repo.get_by_code.return_value = None  # Dept doesn't exist
        new_dept = MagicMock()
        new_dept.name = "Engineering"
        new_dept.is_active = True
        mock_dept_repo.add.return_value = new_dept
        mock_dept_repo_cls.return_value = mock_dept_repo

        mock_adapter = MagicMock()
        mock_adapter.fetch_departments.return_value = [
            HRISDepartment(
                organization_code="ORG1",
                department_code="ENG",
                name="Engineering",
            )
        ]
        mock_adapter.fetch_employees.return_value = []

        from lms.app.integrations.hris.sync_service import HRISSyncService

        service = HRISSyncService(mock_session)
        result = service.sync(mock_adapter, audit_ctx)

        assert result["departments_created"] == 1

    @patch("lms.app.integrations.hris.sync_service.AuditRepository")
    @patch("lms.app.integrations.hris.sync_service.OrganizationRepository")
    @patch("lms.app.integrations.hris.sync_service.DepartmentRepository")
    @patch("lms.app.integrations.hris.sync_service.UserRepository")
    def test_sync_creates_new_user(
        self,
        mock_user_repo_cls,
        mock_dept_repo_cls,
        mock_org_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_org,
        audit_ctx,
    ):
        """sync should create new users."""
        mock_org_repo = MagicMock()
        mock_org_repo.get_by_code.return_value = mock_org
        mock_org_repo_cls.return_value = mock_org_repo

        mock_dept_repo = MagicMock()
        mock_dept_repo_cls.return_value = mock_dept_repo

        mock_user_repo = MagicMock()
        mock_user_repo.get_by_employee_id.return_value = None  # User doesn't exist
        mock_user_repo_cls.return_value = mock_user_repo

        mock_adapter = MagicMock()
        mock_adapter.fetch_departments.return_value = []
        mock_adapter.fetch_employees.return_value = [
            HRISEmployee(
                organization_code="ORG1",
                employee_id="EMP001",
                email="john@example.com",
                first_name="John",
                last_name="Doe",
                department_code=None,
                manager_employee_id=None,
            )
        ]

        from lms.app.integrations.hris.sync_service import HRISSyncService

        service = HRISSyncService(mock_session)
        result = service.sync(mock_adapter, audit_ctx)

        assert result["users_created"] == 1

    @patch("lms.app.integrations.hris.sync_service.AuditRepository")
    @patch("lms.app.integrations.hris.sync_service.OrganizationRepository")
    @patch("lms.app.integrations.hris.sync_service.DepartmentRepository")
    @patch("lms.app.integrations.hris.sync_service.UserRepository")
    def test_ensure_org_returns_none_for_unknown(
        self,
        mock_user_repo_cls,
        mock_dept_repo_cls,
        mock_org_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        audit_ctx,
    ):
        """_ensure_org should return None for unknown org codes."""
        mock_org_repo = MagicMock()
        mock_org_repo.get_by_code.return_value = None
        mock_org_repo_cls.return_value = mock_org_repo

        from lms.app.integrations.hris.sync_service import HRISSyncService

        service = HRISSyncService(mock_session)
        result = service._ensure_org("UNKNOWN", audit_ctx)

        assert result is None

    @patch("lms.app.integrations.hris.sync_service.AuditRepository")
    @patch("lms.app.integrations.hris.sync_service.OrganizationRepository")
    @patch("lms.app.integrations.hris.sync_service.DepartmentRepository")
    @patch("lms.app.integrations.hris.sync_service.UserRepository")
    def test_upsert_department_updates_existing(
        self,
        mock_user_repo_cls,
        mock_dept_repo_cls,
        mock_org_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_org,
        mock_department,
        audit_ctx,
    ):
        """_upsert_department should update existing department."""
        mock_dept_repo = MagicMock()
        mock_dept_repo.get_by_code.return_value = mock_department
        mock_dept_repo_cls.return_value = mock_dept_repo

        from lms.app.integrations.hris.sync_service import HRISSyncService

        service = HRISSyncService(mock_session)

        # Call with updated name
        result = service._upsert_department(
            mock_org,
            HRISDepartment(
                organization_code="ORG1",
                department_code="ENG",
                name="Engineering Updated",  # Changed
                is_active=True,
            ),
            audit_ctx,
        )

        # Should have called update_fields
        mock_dept_repo.update_fields.assert_called_once()

    @patch("lms.app.integrations.hris.sync_service.AuditRepository")
    @patch("lms.app.integrations.hris.sync_service.OrganizationRepository")
    @patch("lms.app.integrations.hris.sync_service.DepartmentRepository")
    @patch("lms.app.integrations.hris.sync_service.UserRepository")
    def test_upsert_department_returns_unchanged(
        self,
        mock_user_repo_cls,
        mock_dept_repo_cls,
        mock_org_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_org,
        mock_department,
        audit_ctx,
    ):
        """_upsert_department should return existing if no changes."""
        mock_dept_repo = MagicMock()
        mock_dept_repo.get_by_code.return_value = mock_department
        mock_dept_repo_cls.return_value = mock_dept_repo

        from lms.app.integrations.hris.sync_service import HRISSyncService

        service = HRISSyncService(mock_session)

        # Call with same data
        result = service._upsert_department(
            mock_org,
            HRISDepartment(
                organization_code="ORG1",
                department_code="ENG",
                name="Engineering",  # Same
                is_active=True,
            ),
            audit_ctx,
        )

        # Should NOT have called update_fields
        mock_dept_repo.update_fields.assert_not_called()
        assert result == mock_department

    @patch("lms.app.integrations.hris.sync_service.AuditRepository")
    @patch("lms.app.integrations.hris.sync_service.OrganizationRepository")
    @patch("lms.app.integrations.hris.sync_service.DepartmentRepository")
    @patch("lms.app.integrations.hris.sync_service.UserRepository")
    def test_upsert_employee_resolves_manager(
        self,
        mock_user_repo_cls,
        mock_dept_repo_cls,
        mock_org_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_org,
        audit_ctx,
    ):
        """_upsert_employee should resolve manager by employee_id."""
        manager = MagicMock()
        manager.id = uuid4()

        mock_user_repo = MagicMock()
        # First call for manager, second for employee
        mock_user_repo.get_by_employee_id.side_effect = [None, manager]
        mock_user_repo_cls.return_value = mock_user_repo

        mock_dept_repo = MagicMock()
        mock_dept_repo_cls.return_value = mock_dept_repo

        from lms.app.integrations.hris.sync_service import HRISSyncService

        service = HRISSyncService(mock_session)

        service._upsert_employee(
            mock_org,
            HRISEmployee(
                organization_code="ORG1",
                employee_id="EMP002",
                email="emp@example.com",
                first_name="Jane",
                last_name="Doe",
                department_code=None,
                manager_employee_id="EMP001",
            ),
            audit_ctx,
        )

        # Should have called get_by_employee_id for manager
        assert mock_user_repo.get_by_employee_id.call_count >= 1
