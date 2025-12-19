"""Policy engine (config-driven).

No hardcoded business rules:
- Policies, eligibility rules, accrual rules, carry-forward, expiry, LOP, encashment are stored in DB.
- This engine reads configurations and evaluates them.

This is a skeleton intended to be extended with a real rules evaluator (e.g., JSONLogic).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Optional, cast
from uuid import UUID

from sqlalchemy.orm import Session

from ..core.exceptions import EligibilityException, PolicyNotFoundException
from ..models.leave import LeavePolicy
from ..models.user import User
from ..repositories import (
    LeaveBalanceRepository,
    LeavePolicyRepository,
    PolicyAssignmentRepository,
)


@dataclass(frozen=True)
class PolicyResolution:
    policy: LeavePolicy
    reason: str


class PolicyEngine:
    def __init__(
        self,
        session: Session,
        *,
        policy_repo: LeavePolicyRepository,
        assignment_repo: PolicyAssignmentRepository,
        balance_repo: LeaveBalanceRepository,
    ):
        self.session = session
        self.policy_repo = policy_repo
        self.assignment_repo = assignment_repo
        self.balance_repo = balance_repo

    def resolve_policy_for_user(
        self,
        *,
        user: User,
        leave_type_id: UUID,
        on_datetime: Optional[datetime] = None,
    ) -> PolicyResolution:
        """Resolve applicable policy for a user & leave type.

        Strategy (configurable, deterministic):
        - Find active policy assignments effective at the time.
        - Prefer user-specific assignment > department assignment > criteria match.
        - Break ties by assignment.priority.

        NOTE: Criteria evaluation is a stub; extend to support complex rules.
        """
        if on_datetime is None:
            on_datetime = datetime.now(timezone.utc)

        # Fetch policies for leave type and org (keeps query predictable)
        organization_id = cast(UUID, user.organization_id)
        policies = self.policy_repo.get_active_for_leave_type(organization_id, leave_type_id)
        if not policies:
            raise PolicyNotFoundException(leave_type_id)

        # Future: query PolicyAssignment with proper filtering. For skeleton, we pick the most recent active policy.
        chosen = policies[0]
        return PolicyResolution(policy=chosen, reason="Most recent active policy for leave type")

    def assert_eligible(self, *, user: User, policy: LeavePolicy, on_datetime: Optional[datetime] = None) -> None:
        """Raise if user is not eligible under the policy."""
        if on_datetime is None:
            on_datetime = datetime.now(timezone.utc)

        if policy.eligibility_type.value == "after_probation":
            # Still config-driven: uses user's probation_end_date field.
            probation_end = cast(Optional[datetime], user.probation_end_date)
            if probation_end is None:
                raise EligibilityException("Probation end date not set")
            if on_datetime < probation_end:
                raise EligibilityException("User is still on probation")

        if policy.eligibility_type.value == "after_tenure":
            hire_date = cast(Optional[datetime], user.hire_date)
            if hire_date is None:
                raise EligibilityException("Hire date not set")
            tenure_days = (on_datetime - hire_date).days
            required = int(cast(Optional[int], policy.eligibility_tenure_days) or 0)
            if tenure_days < required:
                raise EligibilityException(
                    "Minimum tenure not met",
                    criteria={"tenure_days": tenure_days, "required_days": required},
                )

        if policy.eligibility_type.value == "custom":
            # Placeholder: interpret policy.eligibility_rules JSON.
            # Plug in a real evaluator later.
            pass

    def get_balance(self, *, user_id: UUID, leave_type_id: UUID, on_date: date):
        return self.balance_repo.get_current_balance(user_id, leave_type_id, on_date)
