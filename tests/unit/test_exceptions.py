"""Unit tests for LMS exceptions.

Tests:
- Exception construction and attributes
- Error codes and messages
- Details propagation
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from lms.app.core.exceptions import (
    ApprovalException,
    DelegationException,
    EligibilityException,
    EntityNotFoundException,
    EscalationException,
    InsufficientBalanceException,
    LeaveOverlapException,
    LeaveRequestNotFoundException,
    LMSException,
    PolicyNotFoundException,
    PolicyValidationException,
    WorkflowNotFoundException,
    WorkflowStateException,
)


@pytest.mark.unit
class TestLMSException:
    """Tests for base LMSException."""

    def test_basic_exception(self) -> None:
        """Test basic exception creation."""
        exc = LMSException("Test error")

        assert exc.message == "Test error"
        assert exc.error_code == "LMS_ERROR"
        assert exc.details == {}

    def test_exception_with_code_and_details(self) -> None:
        """Test exception with custom error code and details."""
        exc = LMSException(
            message="Custom error", error_code="CUSTOM_CODE", details={"key": "value"}
        )

        assert exc.message == "Custom error"
        assert exc.error_code == "CUSTOM_CODE"
        assert exc.details == {"key": "value"}

    def test_exception_str(self) -> None:
        """Test exception string representation."""
        exc = LMSException("Test error message")
        assert str(exc) == "Test error message"


@pytest.mark.unit
class TestPolicyExceptions:
    """Tests for policy-related exceptions."""

    def test_policy_not_found(self) -> None:
        """Test PolicyNotFoundException."""
        policy_id = uuid4()
        exc = PolicyNotFoundException(policy_id)

        assert exc.error_code == "POLICY_NOT_FOUND"
        assert str(policy_id) in exc.details["policy_id"]

    def test_policy_validation_exception(self) -> None:
        """Test PolicyValidationException."""
        exc = PolicyValidationException(
            message="Validation failed",
            violations=["min_days_notice not met", "max_days exceeded"],
        )

        assert exc.error_code == "POLICY_VALIDATION_FAILED"
        assert len(exc.details["violations"]) == 2

    def test_insufficient_balance(self) -> None:
        """Test InsufficientBalanceException."""
        exc = InsufficientBalanceException(
            available=5.0, requested=10.0, leave_type="ANNUAL"
        )

        assert exc.error_code == "INSUFFICIENT_BALANCE"
        assert exc.details["available"] == 5.0
        assert exc.details["requested"] == 10.0
        assert exc.details["leave_type"] == "ANNUAL"
        assert "5" in str(exc) and "10" in str(exc)

    def test_eligibility_exception(self) -> None:
        """Test EligibilityException."""
        exc = EligibilityException(
            message="Minimum tenure not met",
            criteria={"tenure_days": 30, "required_days": 90},
        )

        assert exc.error_code == "ELIGIBILITY_NOT_MET"
        assert exc.details["criteria"]["tenure_days"] == 30

    def test_eligibility_exception_no_criteria(self) -> None:
        """Test EligibilityException without criteria."""
        exc = EligibilityException("User is on probation")

        assert exc.error_code == "ELIGIBILITY_NOT_MET"
        assert exc.details["criteria"] == {}


@pytest.mark.unit
class TestWorkflowExceptions:
    """Tests for workflow-related exceptions."""

    def test_workflow_not_found_with_id(self) -> None:
        """Test WorkflowNotFoundException with workflow_id."""
        workflow_id = uuid4()
        exc = WorkflowNotFoundException(workflow_id=workflow_id)

        assert exc.error_code == "WORKFLOW_NOT_FOUND"
        assert str(workflow_id) in exc.details["workflow_id"]

    def test_workflow_not_found_with_leave_type(self) -> None:
        """Test WorkflowNotFoundException with leave_type."""
        exc = WorkflowNotFoundException(leave_type="ANNUAL")

        assert exc.error_code == "WORKFLOW_NOT_FOUND"
        assert exc.details["leave_type"] == "ANNUAL"

    def test_workflow_state_exception(self) -> None:
        """Test WorkflowStateException."""
        exc = WorkflowStateException(current_state="DRAFT", attempted_action="approve")

        assert exc.error_code == "INVALID_STATE_TRANSITION"
        assert "DRAFT" in str(exc)
        assert "approve" in str(exc)

    def test_approval_exception(self) -> None:
        """Test ApprovalException."""
        approver_id = uuid4()
        exc = ApprovalException(
            message="Not authorized to approve", approver_id=approver_id
        )

        assert exc.error_code == "APPROVAL_FAILED"
        assert str(approver_id) in exc.details["approver_id"]

    def test_approval_exception_no_approver(self) -> None:
        """Test ApprovalException without approver_id."""
        exc = ApprovalException("Step already approved")

        assert exc.error_code == "APPROVAL_FAILED"
        assert exc.details["approver_id"] is None

    def test_delegation_exception(self) -> None:
        """Test DelegationException."""
        exc = DelegationException("Cannot delegate to self")

        assert exc.error_code == "DELEGATION_FAILED"
        assert "self" in str(exc)

    def test_escalation_exception(self) -> None:
        """Test EscalationException."""
        exc = EscalationException("No higher approver available")

        assert exc.error_code == "ESCALATION_FAILED"


@pytest.mark.unit
class TestLeaveExceptions:
    """Tests for leave-related exceptions."""

    def test_leave_request_not_found(self) -> None:
        """Test LeaveRequestNotFoundException."""
        request_id = uuid4()
        exc = LeaveRequestNotFoundException(request_id)

        assert exc.error_code == "LEAVE_REQUEST_NOT_FOUND"
        assert str(request_id) in exc.details["request_id"]

    def test_leave_overlap_exception(self) -> None:
        """Test LeaveOverlapException."""
        overlaps = [
            {"request_id": str(uuid4()), "dates": "2024-01-15 to 2024-01-17"},
            {"request_id": str(uuid4()), "dates": "2024-01-20 to 2024-01-22"},
        ]
        exc = LeaveOverlapException(overlaps)

        assert exc.error_code == "LEAVE_OVERLAP"
        assert len(exc.details["overlapping_dates"]) == 2


@pytest.mark.unit
class TestEntityNotFoundException:
    """Tests for EntityNotFoundException."""

    def test_entity_not_found(self) -> None:
        """Test EntityNotFoundException."""
        entity_id = uuid4()
        exc = EntityNotFoundException("User", entity_id)

        assert exc.error_code == "ENTITY_NOT_FOUND"
        assert "User" in str(exc)
        assert exc.details["entity_type"] == "User"
        assert str(entity_id) in exc.details["entity_id"]

    def test_entity_not_found_with_string_id(self) -> None:
        """Test EntityNotFoundException with string ID."""
        exc = EntityNotFoundException("LeaveType", "ANNUAL")

        assert exc.details["entity_id"] == "ANNUAL"
