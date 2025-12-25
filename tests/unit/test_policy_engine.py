"""Unit tests for PolicyEngine.

Tests:
- Policy resolution for users
- Eligibility checking (probation, tenure, custom)
- Edge cases and error handling
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from lms.app.core.enums import EligibilityType
from lms.app.core.exceptions import EligibilityException, PolicyNotFoundException
from lms.app.engines.policy_engine import PolicyEngine
from tests.conftest import (
    FakeLeaveBalance,
    FakeLeavePolicy,
    FakeLeavePolicyRepository,
    FakeSession,
    FakeUser,
)


class FakePolicyAssignmentRepository:
    """Fake policy assignment repository."""

    pass


@pytest.fixture
def policy_engine(
    fake_session: FakeSession,
    fake_policy_repo: FakeLeavePolicyRepository,
    fake_balance_repo,
) -> PolicyEngine:
    """Provide a PolicyEngine with fake repositories."""
    return PolicyEngine(
        fake_session,  # type: ignore[arg-type]
        policy_repo=fake_policy_repo,  # type: ignore[arg-type]
        assignment_repo=FakePolicyAssignmentRepository(),  # type: ignore[arg-type]
        balance_repo=fake_balance_repo,  # type: ignore[arg-type]
    )


@pytest.mark.unit
class TestPolicyResolution:
    """Tests for policy resolution."""

    def test_resolve_policy_returns_active_policy(
        self,
        policy_engine: PolicyEngine,
        fake_policy_repo: FakeLeavePolicyRepository,
        fake_user: FakeUser,
        fake_leave_policy: FakeLeavePolicy,
    ) -> None:
        """Test that resolve_policy_for_user returns an active policy."""
        # Add policy to repo
        fake_policy_repo._entities[fake_leave_policy.id] = fake_leave_policy

        # Ensure policy matches user's org and leave type
        fake_leave_policy.organization_id = fake_user.organization_id

        resolution = policy_engine.resolve_policy_for_user(
            user=fake_user,  # type: ignore[arg-type]
            leave_type_id=fake_leave_policy.leave_type_id,
        )

        assert resolution.policy == fake_leave_policy
        assert "active policy" in resolution.reason.lower()

    def test_resolve_policy_raises_when_no_policy_found(
        self,
        policy_engine: PolicyEngine,
        fake_user: FakeUser,
    ) -> None:
        """Test that PolicyNotFoundException is raised when no policy exists."""
        with pytest.raises(PolicyNotFoundException) as exc_info:
            policy_engine.resolve_policy_for_user(
                user=fake_user,  # type: ignore[arg-type]
                leave_type_id=uuid4(),
            )

        assert "POLICY_NOT_FOUND" in str(exc_info.value.error_code)


@pytest.mark.unit
class TestEligibilityChecks:
    """Tests for eligibility assertion."""

    def test_immediate_eligibility_always_passes(
        self,
        policy_engine: PolicyEngine,
        fake_user: FakeUser,
    ) -> None:
        """Test that immediate eligibility type always passes."""
        policy = FakeLeavePolicy(eligibility_type=EligibilityType.IMMEDIATE)

        # Should not raise
        policy_engine.assert_eligible(
            user=fake_user,  # type: ignore[arg-type]
            policy=policy,  # type: ignore[arg-type]
        )

    def test_after_probation_passes_when_probation_ended(
        self,
        policy_engine: PolicyEngine,
    ) -> None:
        """Test that after_probation passes when user's probation has ended."""
        user = FakeUser(
            probation_end_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )
        policy = FakeLeavePolicy(eligibility_type=EligibilityType.AFTER_PROBATION)

        # Check eligibility at a date after probation
        check_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Should not raise
        policy_engine.assert_eligible(
            user=user,  # type: ignore[arg-type]
            policy=policy,  # type: ignore[arg-type]
            on_datetime=check_date,
        )

    def test_after_probation_fails_during_probation(
        self,
        policy_engine: PolicyEngine,
    ) -> None:
        """Test that after_probation fails when user is still on probation."""
        user = FakeUser(
            probation_end_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )
        policy = FakeLeavePolicy(eligibility_type=EligibilityType.AFTER_PROBATION)

        # Check eligibility at a date before probation ends
        check_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

        with pytest.raises(EligibilityException) as exc_info:
            policy_engine.assert_eligible(
                user=user,  # type: ignore[arg-type]
                policy=policy,  # type: ignore[arg-type]
                on_datetime=check_date,
            )

        assert "probation" in str(exc_info.value).lower()

    def test_after_probation_fails_when_probation_date_not_set(
        self,
        policy_engine: PolicyEngine,
    ) -> None:
        """Test that after_probation fails when probation_end_date is not set."""
        user = FakeUser(probation_end_date=None)
        policy = FakeLeavePolicy(eligibility_type=EligibilityType.AFTER_PROBATION)

        with pytest.raises(EligibilityException) as exc_info:
            policy_engine.assert_eligible(
                user=user,  # type: ignore[arg-type]
                policy=policy,  # type: ignore[arg-type]
            )

        assert "not set" in str(exc_info.value).lower()

    def test_after_tenure_passes_when_tenure_met(
        self,
        policy_engine: PolicyEngine,
    ) -> None:
        """Test that after_tenure passes when minimum tenure is met."""
        user = FakeUser(
            hire_date=datetime(2022, 1, 1, tzinfo=timezone.utc),
        )
        policy = FakeLeavePolicy(
            eligibility_type=EligibilityType.AFTER_TENURE,
            eligibility_tenure_days=365,  # 1 year
        )

        # Check eligibility after 2 years
        check_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Should not raise
        policy_engine.assert_eligible(
            user=user,  # type: ignore[arg-type]
            policy=policy,  # type: ignore[arg-type]
            on_datetime=check_date,
        )

    def test_after_tenure_fails_when_tenure_not_met(
        self,
        policy_engine: PolicyEngine,
    ) -> None:
        """Test that after_tenure fails when minimum tenure is not met."""
        user = FakeUser(
            hire_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
        )
        policy = FakeLeavePolicy(
            eligibility_type=EligibilityType.AFTER_TENURE,
            eligibility_tenure_days=365,  # 1 year
        )

        # Check eligibility after only 6 months
        check_date = datetime(2024, 12, 1, tzinfo=timezone.utc)

        with pytest.raises(EligibilityException) as exc_info:
            policy_engine.assert_eligible(
                user=user,  # type: ignore[arg-type]
                policy=policy,  # type: ignore[arg-type]
                on_datetime=check_date,
            )

        assert "tenure" in str(exc_info.value).lower()

    def test_after_tenure_fails_when_hire_date_not_set(
        self,
        policy_engine: PolicyEngine,
    ) -> None:
        """Test that after_tenure fails when hire_date is not set."""
        user = FakeUser(hire_date=None)
        policy = FakeLeavePolicy(
            eligibility_type=EligibilityType.AFTER_TENURE,
            eligibility_tenure_days=365,
        )

        with pytest.raises(EligibilityException) as exc_info:
            policy_engine.assert_eligible(
                user=user,  # type: ignore[arg-type]
                policy=policy,  # type: ignore[arg-type]
            )

        assert "hire date" in str(exc_info.value).lower()

    def test_custom_eligibility_passes(
        self,
        policy_engine: PolicyEngine,
        fake_user: FakeUser,
    ) -> None:
        """Test that custom eligibility type passes (placeholder)."""
        policy = FakeLeavePolicy(eligibility_type=EligibilityType.CUSTOM)

        # Current skeleton implementation passes custom eligibility
        policy_engine.assert_eligible(
            user=fake_user,  # type: ignore[arg-type]
            policy=policy,  # type: ignore[arg-type]
        )


@pytest.mark.unit
class TestBalanceRetrieval:
    """Tests for balance retrieval."""

    def test_get_balance_returns_balance(
        self,
        policy_engine: PolicyEngine,
        fake_balance_repo,
        fake_leave_balance: FakeLeaveBalance,
    ) -> None:
        """Test that get_balance returns the user's balance."""
        fake_balance_repo._entities[fake_leave_balance.id] = fake_leave_balance

        from datetime import date

        balance = policy_engine.get_balance(
            user_id=fake_leave_balance.user_id,
            leave_type_id=fake_leave_balance.leave_type_id,
            on_date=date.today(),
        )

        assert balance == fake_leave_balance

    def test_get_balance_returns_none_when_not_found(
        self,
        policy_engine: PolicyEngine,
    ) -> None:
        """Test that get_balance returns None when balance not found."""
        from datetime import date

        balance = policy_engine.get_balance(
            user_id=uuid4(),
            leave_type_id=uuid4(),
            on_date=date.today(),
        )

        assert balance is None
