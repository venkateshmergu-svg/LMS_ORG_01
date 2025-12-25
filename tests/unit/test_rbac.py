"""Unit tests for RBAC module."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.core.enums import UserRole
from lms.app.core.rbac import RBACContext, require_all_roles, require_roles
from lms.app.core.security import AuthenticatedUser


class TestRBACContext:
    """Tests for RBACContext class."""

    @pytest.fixture
    def employee_user(self):
        """Create an employee user."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="employee@example.com",
            organization_id=uuid4(),
            roles=[UserRole.EMPLOYEE],
        )

    @pytest.fixture
    def manager_user(self):
        """Create a manager user."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="manager@example.com",
            organization_id=uuid4(),
            roles=[UserRole.EMPLOYEE, UserRole.MANAGER],
        )

    @pytest.fixture
    def hr_admin_user(self):
        """Create an HR admin user."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="hr@example.com",
            organization_id=uuid4(),
            roles=[UserRole.EMPLOYEE, UserRole.HR_ADMIN],
        )

    @pytest.fixture
    def system_admin_user(self):
        """Create a system admin user."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="admin@example.com",
            organization_id=uuid4(),
            roles=[UserRole.SYSTEM_ADMIN],
        )

    @pytest.fixture
    def auditor_user(self):
        """Create an auditor user."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="auditor@example.com",
            organization_id=uuid4(),
            roles=[UserRole.AUDITOR],
        )

    @pytest.fixture
    def multi_role_user(self):
        """Create a user with multiple roles."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="multi@example.com",
            organization_id=uuid4(),
            roles=[UserRole.EMPLOYEE, UserRole.MANAGER, UserRole.HR_ADMIN],
        )

    def test_context_initializes_correctly(self, employee_user):
        """RBACContext should initialize with user details."""
        ctx = RBACContext(employee_user)

        assert ctx.user == employee_user
        assert ctx.user_id == employee_user.user_id
        assert ctx.roles == employee_user.roles
        assert ctx.organization_id == employee_user.organization_id

    def test_has_role_returns_true_when_has_role(self, employee_user):
        """has_role should return True when user has the role."""
        ctx = RBACContext(employee_user)

        assert ctx.has_role(UserRole.EMPLOYEE) is True

    def test_has_role_returns_false_when_missing_role(self, employee_user):
        """has_role should return False when user doesn't have the role."""
        ctx = RBACContext(employee_user)

        assert ctx.has_role(UserRole.MANAGER) is False

    def test_has_role_with_multiple_options(self, manager_user):
        """has_role should return True if user has any of the roles."""
        ctx = RBACContext(manager_user)

        assert ctx.has_role(UserRole.MANAGER, UserRole.HR_ADMIN) is True
        assert ctx.has_role(UserRole.HR_ADMIN, UserRole.SYSTEM_ADMIN) is False

    def test_has_all_roles_returns_true_when_has_all(self, multi_role_user):
        """has_all_roles should return True when user has all roles."""
        ctx = RBACContext(multi_role_user)

        assert ctx.has_all_roles(UserRole.EMPLOYEE, UserRole.MANAGER) is True

    def test_has_all_roles_returns_false_when_missing_one(self, multi_role_user):
        """has_all_roles should return False when user misses any role."""
        ctx = RBACContext(multi_role_user)

        assert ctx.has_all_roles(UserRole.MANAGER, UserRole.SYSTEM_ADMIN) is False

    def test_is_system_admin(self, system_admin_user, employee_user):
        """is_system_admin should check for SYSTEM_ADMIN role."""
        admin_ctx = RBACContext(system_admin_user)
        employee_ctx = RBACContext(employee_user)

        assert admin_ctx.is_system_admin() is True
        assert employee_ctx.is_system_admin() is False

    def test_is_hr_admin(self, hr_admin_user, employee_user):
        """is_hr_admin should check for HR_ADMIN role."""
        hr_ctx = RBACContext(hr_admin_user)
        employee_ctx = RBACContext(employee_user)

        assert hr_ctx.is_hr_admin() is True
        assert employee_ctx.is_hr_admin() is False

    def test_is_manager(self, manager_user, employee_user):
        """is_manager should check for MANAGER role."""
        manager_ctx = RBACContext(manager_user)
        employee_ctx = RBACContext(employee_user)

        assert manager_ctx.is_manager() is True
        assert employee_ctx.is_manager() is False

    def test_is_employee(self, employee_user, system_admin_user):
        """is_employee should check for EMPLOYEE role."""
        employee_ctx = RBACContext(employee_user)
        admin_ctx = RBACContext(system_admin_user)

        assert employee_ctx.is_employee() is True
        assert admin_ctx.is_employee() is False

    def test_is_auditor(self, auditor_user, employee_user):
        """is_auditor should check for AUDITOR role."""
        auditor_ctx = RBACContext(auditor_user)
        employee_ctx = RBACContext(employee_user)

        assert auditor_ctx.is_auditor() is True
        assert employee_ctx.is_auditor() is False
