"""Unit tests for LMS enums.

Tests:
- All enum values are defined
- String enum conversion
- Enum comparisons
"""

from __future__ import annotations

import pytest

from lms.app.core.enums import (
    AccrualFrequency,
    AuditAction,
    CarryForwardType,
    EligibilityType,
    LeaveRequestStatus,
    LeaveUnit,
    NotificationType,
    UserRole,
    UserStatus,
    WorkflowStepStatus,
)


@pytest.mark.unit
class TestUserRole:
    """Tests for UserRole enum."""

    def test_all_roles_defined(self) -> None:
        """Test that all expected roles are defined."""
        expected_roles = {"employee", "manager", "hr_admin", "system_admin", "auditor"}
        actual_roles = {role.value for role in UserRole}

        assert actual_roles == expected_roles

    def test_role_string_conversion(self) -> None:
        """Test that roles convert to strings correctly."""
        assert UserRole.EMPLOYEE.value == "employee"
        assert UserRole.MANAGER.value == "manager"
        assert UserRole.HR_ADMIN.value == "hr_admin"
        assert UserRole.SYSTEM_ADMIN.value == "system_admin"
        assert UserRole.AUDITOR.value == "auditor"

    def test_role_comparison(self) -> None:
        """Test role comparisons."""
        assert UserRole.EMPLOYEE == UserRole.EMPLOYEE
        assert UserRole.EMPLOYEE != UserRole.MANAGER


@pytest.mark.unit
class TestUserStatus:
    """Tests for UserStatus enum."""

    def test_all_statuses_defined(self) -> None:
        """Test that all expected statuses are defined."""
        expected = {"active", "inactive", "suspended", "terminated"}
        actual = {status.value for status in UserStatus}

        assert actual == expected

    def test_status_string_conversion(self) -> None:
        """Test status string conversion."""
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.TERMINATED.value == "terminated"


@pytest.mark.unit
class TestLeaveRequestStatus:
    """Tests for LeaveRequestStatus enum."""

    def test_all_statuses_defined(self) -> None:
        """Test that all expected leave request statuses are defined."""
        expected = {
            "draft",
            "pending_approval",
            "approved",
            "rejected",
            "cancelled",
            "withdrawn",
        }
        actual = {status.value for status in LeaveRequestStatus}

        assert actual == expected

    def test_workflow_states(self) -> None:
        """Test workflow state values."""
        assert LeaveRequestStatus.DRAFT.value == "draft"
        assert LeaveRequestStatus.PENDING_APPROVAL.value == "pending_approval"
        assert LeaveRequestStatus.APPROVED.value == "approved"
        assert LeaveRequestStatus.REJECTED.value == "rejected"
        assert LeaveRequestStatus.CANCELLED.value == "cancelled"
        assert LeaveRequestStatus.WITHDRAWN.value == "withdrawn"


@pytest.mark.unit
class TestWorkflowStepStatus:
    """Tests for WorkflowStepStatus enum."""

    def test_all_step_statuses_defined(self) -> None:
        """Test that all expected workflow step statuses are defined."""
        expected = {
            "pending",
            "approved",
            "rejected",
            "skipped",
            "escalated",
            "delegated",
        }
        actual = {status.value for status in WorkflowStepStatus}

        assert actual == expected


@pytest.mark.unit
class TestAccrualFrequency:
    """Tests for AccrualFrequency enum."""

    def test_all_frequencies_defined(self) -> None:
        """Test that all expected accrual frequencies are defined."""
        expected = {
            "daily",
            "weekly",
            "bi_weekly",
            "monthly",
            "quarterly",
            "semi_annually",
            "annually",
            "one_time",
        }
        actual = {freq.value for freq in AccrualFrequency}

        assert actual == expected


@pytest.mark.unit
class TestLeaveUnit:
    """Tests for LeaveUnit enum."""

    def test_units_defined(self) -> None:
        """Test that leave units are defined."""
        assert LeaveUnit.DAYS.value == "days"
        assert LeaveUnit.HOURS.value == "hours"


@pytest.mark.unit
class TestCarryForwardType:
    """Tests for CarryForwardType enum."""

    def test_all_types_defined(self) -> None:
        """Test that all carry forward types are defined."""
        expected = {"none", "unlimited", "capped", "percentage"}
        actual = {cf.value for cf in CarryForwardType}

        assert actual == expected


@pytest.mark.unit
class TestEligibilityType:
    """Tests for EligibilityType enum."""

    def test_all_types_defined(self) -> None:
        """Test that all eligibility types are defined."""
        expected = {"immediate", "after_probation", "after_tenure", "custom"}
        actual = {et.value for et in EligibilityType}

        assert actual == expected


@pytest.mark.unit
class TestAuditAction:
    """Tests for AuditAction enum."""

    def test_all_actions_defined(self) -> None:
        """Test that all expected audit actions are defined."""
        expected_actions = {
            "create",
            "update",
            "delete",
            "status_change",
            "approval",
            "rejection",
            "delegation",
            "escalation",
            "accrual",
            "adjustment",
            "encashment",
            "carry_forward",
            "expiry",
            "login",
            "logout",
        }
        actual_actions = {action.value for action in AuditAction}

        assert actual_actions == expected_actions


@pytest.mark.unit
class TestNotificationType:
    """Tests for NotificationType enum."""

    def test_notification_types_defined(self) -> None:
        """Test that notification types are defined."""
        assert NotificationType.EMAIL.value == "email"
        assert NotificationType.IN_APP.value == "in_app"


@pytest.mark.unit
class TestEnumMembership:
    """Tests for enum membership checks."""

    def test_string_enum_membership(self) -> None:
        """Test that string values can be used for membership checks."""
        # UserRole inherits from str, so this works
        assert "employee" in [role.value for role in UserRole]
        assert "unknown_role" not in [role.value for role in UserRole]

    def test_enum_iteration(self) -> None:
        """Test that enums can be iterated."""
        roles = list(UserRole)
        assert len(roles) == 5
        assert UserRole.EMPLOYEE in roles

    def test_enum_from_string(self) -> None:
        """Test creating enum from string value."""
        role = UserRole("employee")
        assert role == UserRole.EMPLOYEE

        status = LeaveRequestStatus("approved")
        assert status == LeaveRequestStatus.APPROVED
