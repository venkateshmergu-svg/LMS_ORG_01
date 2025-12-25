"""Shared pytest fixtures for the LMS test suite.

Provides:
- Fake/mock implementations for unit tests
- Test client for integration tests
- Auth stub fixtures
- Database fixtures (for integration tests)
- Audit context fixtures
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Optional
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from lms.app.core.enums import (
    AuditAction,
    EligibilityType,
    LeaveRequestStatus,
    UserRole,
    UserStatus,
    WorkflowStepStatus,
)
from lms.app.repositories import AuditContext

# ==============================================================================
# Fake Model Classes (for unit testing without SQLAlchemy)
# ==============================================================================


@dataclass
class FakeOrganization:
    """Fake organization without SQLAlchemy columns."""

    id: UUID = field(default_factory=uuid4)
    name: str = "Test Organization"
    code: str = "TEST_ORG"
    is_active: bool = True


@dataclass
class FakeDepartment:
    """Fake department without SQLAlchemy columns."""

    id: UUID = field(default_factory=uuid4)
    organization_id: UUID = field(default_factory=uuid4)
    name: str = "Engineering"
    code: str = "ENG"
    is_active: bool = True


@dataclass
class FakeUser:
    """Fake user without SQLAlchemy columns."""

    id: UUID = field(default_factory=uuid4)
    organization_id: UUID = field(default_factory=uuid4)
    department_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    email: str = "test@example.com"
    first_name: str = "Test"
    last_name: str = "User"
    role: UserRole = UserRole.EMPLOYEE
    status: UserStatus = UserStatus.ACTIVE
    hire_date: Optional[datetime] = None
    probation_end_date: Optional[datetime] = None


@dataclass
class FakeLeaveType:
    """Fake leave type without SQLAlchemy columns."""

    id: UUID = field(default_factory=uuid4)
    organization_id: UUID = field(default_factory=uuid4)
    code: str = "ANNUAL"
    name: str = "Annual Leave"
    is_active: bool = True


@dataclass
class FakeLeavePolicy:
    """Fake leave policy without SQLAlchemy columns."""

    id: UUID = field(default_factory=uuid4)
    organization_id: UUID = field(default_factory=uuid4)
    leave_type_id: UUID = field(default_factory=uuid4)
    name: str = "Standard Annual Leave Policy"
    annual_entitlement: float = 20.0
    eligibility_type: EligibilityType = EligibilityType.IMMEDIATE
    eligibility_tenure_days: Optional[int] = None
    is_active: bool = True
    effective_from: date = field(default_factory=lambda: date(2024, 1, 1))
    effective_to: Optional[date] = None


@dataclass
class FakeLeaveBalance:
    """Fake leave balance without SQLAlchemy columns."""

    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    leave_type_id: UUID = field(default_factory=uuid4)
    policy_id: UUID = field(default_factory=uuid4)
    year: int = 2024
    opening_balance: float = 20.0
    accrued: float = 0.0
    used: float = 0.0
    pending: float = 0.0
    adjusted: float = 0.0
    carried_forward: float = 0.0
    encashed: float = 0.0
    expired: float = 0.0
    leave_type: Optional[FakeLeaveType] = None

    @property
    def available_balance(self) -> float:
        """Calculate available balance."""
        return float(
            self.opening_balance
            + self.accrued
            + self.carried_forward
            + self.adjusted
            - self.used
            - self.pending
            - self.encashed
            - self.expired
        )


@dataclass
class FakeLeaveRequest:
    """Fake leave request without SQLAlchemy columns."""

    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    leave_type_id: UUID = field(default_factory=uuid4)
    policy_id: UUID = field(default_factory=uuid4)
    request_number: str = "LR-TEST001"
    start_date: date = field(default_factory=lambda: date(2024, 1, 15))
    end_date: date = field(default_factory=lambda: date(2024, 1, 17))
    total_days: float = 3.0
    reason: Optional[str] = "Test leave"
    status: LeaveRequestStatus = LeaveRequestStatus.DRAFT
    submitted_at: Optional[datetime] = None


@dataclass
class FakeWorkflowStep:
    """Fake workflow step without SQLAlchemy columns."""

    id: UUID = field(default_factory=uuid4)
    leave_request_id: UUID = field(default_factory=uuid4)
    workflow_id: UUID = field(default_factory=uuid4)
    step_order: int = 1
    approver_id: UUID = field(default_factory=uuid4)
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    assigned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    acted_at: Optional[datetime] = None
    comment: Optional[str] = None


@dataclass
class FakeWorkflowConfiguration:
    """Fake workflow configuration without SQLAlchemy columns."""

    id: UUID = field(default_factory=uuid4)
    organization_id: UUID = field(default_factory=uuid4)
    leave_type_id: Optional[UUID] = None
    name: str = "Standard Approval Workflow"
    is_active: bool = True


# ==============================================================================
# Fake Session and Transaction
# ==============================================================================


class FakeTransaction:
    """Fake SQLAlchemy transaction."""

    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class FakeSession:
    """Fake SQLAlchemy session for unit testing."""

    def __init__(self) -> None:
        self._tx: Optional[FakeTransaction] = None
        self.closed = False
        self.begin_calls = 0
        self.is_active = True
        self._entities: dict[type, dict[UUID, Any]] = {}
        self._flushed_entities: list[Any] = []

    def begin(self) -> FakeTransaction:
        self.begin_calls += 1
        self._tx = FakeTransaction()
        return self._tx

    def add(self, entity: Any) -> None:
        """Add entity to session."""
        entity_type = type(entity)
        if entity_type not in self._entities:
            self._entities[entity_type] = {}
        if hasattr(entity, "id"):
            self._entities[entity_type][entity.id] = entity

    def flush(self) -> None:
        """Flush pending changes."""
        pass

    def get(self, model: type, entity_id: UUID) -> Optional[Any]:
        """Get entity by ID."""
        if model in self._entities:
            return self._entities[model].get(entity_id)
        return None

    def execute(self, stmt: Any) -> MagicMock:
        """Execute a statement (returns mock)."""
        mock = MagicMock()
        mock.scalars.return_value.all.return_value = []
        mock.scalar.return_value = 0
        return mock

    def close(self) -> None:
        self.closed = True
        self.is_active = False


# ==============================================================================
# Fake Repository Classes
# ==============================================================================


class FakeBaseRepository:
    """Base fake repository with common operations."""

    def __init__(self) -> None:
        self._entities: dict[UUID, Any] = {}
        self._updates: list[dict[str, Any]] = []

    def get(self, entity_id: UUID) -> Optional[Any]:
        return self._entities.get(entity_id)

    def get_required(self, entity_id: UUID) -> Any:
        entity = self.get(entity_id)
        if entity is None:
            from lms.app.core.exceptions import EntityNotFoundException

            raise EntityNotFoundException("Entity", entity_id)
        return entity

    def add(
        self, entity: Any, *, ctx: AuditContext, description: str | None = None
    ) -> Any:
        if hasattr(entity, "id"):
            self._entities[entity.id] = entity
        return entity

    def update_fields(
        self,
        entity: Any,
        fields: dict[str, Any],
        *,
        ctx: AuditContext,
        description: str | None = None,
    ) -> Any:
        self._updates.append(
            {
                "entity_id": getattr(entity, "id", None),
                "fields": fields,
                "description": description,
            }
        )
        for key, value in fields.items():
            setattr(entity, key, value)
        return entity

    def list(self, *, limit: int = 100, offset: int = 0) -> list[Any]:
        return list(self._entities.values())[offset : offset + limit]

    def count(self) -> int:
        return len(self._entities)


class FakeUserRepository(FakeBaseRepository):
    """Fake user repository."""

    def get_by_email(self, email: str) -> Optional[FakeUser]:
        for user in self._entities.values():
            if hasattr(user, "email") and user.email == email:
                return user
        return None


class FakeLeaveRequestRepository(FakeBaseRepository):
    """Fake leave request repository."""

    def find_overlaps(
        self, user_id: UUID, start_date: date, end_date: date
    ) -> list[FakeLeaveRequest]:
        """Find overlapping leave requests."""
        overlaps = []
        for req in self._entities.values():
            if (
                hasattr(req, "user_id")
                and req.user_id == user_id
                and req.start_date <= end_date
                and req.end_date >= start_date
            ):
                overlaps.append(req)
        return overlaps

    def list_for_user(
        self, user_id: UUID, *, limit: int = 100, offset: int = 0
    ) -> list[FakeLeaveRequest]:
        return [
            req
            for req in self._entities.values()
            if hasattr(req, "user_id") and req.user_id == user_id
        ][offset : offset + limit]


class FakeLeaveBalanceRepository(FakeBaseRepository):
    """Fake leave balance repository."""

    def get_current_balance(
        self, user_id: UUID, leave_type_id: UUID, on_date: date
    ) -> Optional[FakeLeaveBalance]:
        for balance in self._entities.values():
            if (
                hasattr(balance, "user_id")
                and balance.user_id == user_id
                and balance.leave_type_id == leave_type_id
            ):
                return balance
        return None


class FakeLeavePolicyRepository(FakeBaseRepository):
    """Fake leave policy repository."""

    def get_active_for_leave_type(
        self, organization_id: UUID, leave_type_id: UUID
    ) -> list[FakeLeavePolicy]:
        return [
            policy
            for policy in self._entities.values()
            if (
                hasattr(policy, "organization_id")
                and policy.organization_id == organization_id
                and policy.leave_type_id == leave_type_id
                and policy.is_active
            )
        ]


class FakeWorkflowStepRepository(FakeBaseRepository):
    """Fake workflow step repository."""

    def list_pending_for_approver(self, approver_id: UUID) -> list[FakeWorkflowStep]:
        return [
            step
            for step in self._entities.values()
            if (
                hasattr(step, "approver_id")
                and step.approver_id == approver_id
                and step.status == WorkflowStepStatus.PENDING
            )
        ]


class FakeAuditRepository(FakeBaseRepository):
    """Fake audit repository that records audit events."""

    def __init__(self) -> None:
        super().__init__()
        self.audit_events: list[dict[str, Any]] = []

    def log(
        self,
        *,
        action: AuditAction,
        entity_type: str,
        entity_id: UUID,
        ctx: AuditContext,
        old_values: Optional[dict[str, Any]] = None,
        new_values: Optional[dict[str, Any]] = None,
        description: Optional[str] = None,
    ) -> None:
        self.audit_events.append(
            {
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "actor_id": ctx.actor_id,
                "old_values": old_values,
                "new_values": new_values,
                "description": description,
            }
        )


# ==============================================================================
# Pytest Fixtures
# ==============================================================================


@pytest.fixture
def fake_session() -> FakeSession:
    """Provide a fake SQLAlchemy session."""
    return FakeSession()


@pytest.fixture
def fake_transaction() -> FakeTransaction:
    """Provide a fake transaction."""
    return FakeTransaction()


@pytest.fixture
def audit_ctx() -> AuditContext:
    """Provide a standard audit context."""
    return AuditContext(actor_id=uuid4(), actor_type="user")


@pytest.fixture
def system_ctx() -> AuditContext:
    """Provide a system audit context."""
    return AuditContext(actor_id=uuid4(), actor_type="system")


@pytest.fixture
def fake_organization() -> FakeOrganization:
    """Provide a fake organization."""
    return FakeOrganization()


@pytest.fixture
def fake_user(fake_organization: FakeOrganization) -> FakeUser:
    """Provide a fake user."""
    return FakeUser(
        organization_id=fake_organization.id,
        hire_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
        probation_end_date=datetime(2023, 4, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def fake_manager(fake_organization: FakeOrganization) -> FakeUser:
    """Provide a fake manager user."""
    return FakeUser(
        organization_id=fake_organization.id,
        email="manager@example.com",
        first_name="Manager",
        role=UserRole.MANAGER,
        hire_date=datetime(2022, 1, 1, tzinfo=timezone.utc),
        probation_end_date=datetime(2022, 4, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def fake_leave_type(fake_organization: FakeOrganization) -> FakeLeaveType:
    """Provide a fake leave type."""
    return FakeLeaveType(organization_id=fake_organization.id)


@pytest.fixture
def fake_leave_policy(
    fake_organization: FakeOrganization, fake_leave_type: FakeLeaveType
) -> FakeLeavePolicy:
    """Provide a fake leave policy."""
    return FakeLeavePolicy(
        organization_id=fake_organization.id,
        leave_type_id=fake_leave_type.id,
    )


@pytest.fixture
def fake_leave_balance(
    fake_user: FakeUser,
    fake_leave_type: FakeLeaveType,
    fake_leave_policy: FakeLeavePolicy,
) -> FakeLeaveBalance:
    """Provide a fake leave balance."""
    return FakeLeaveBalance(
        user_id=fake_user.id,
        leave_type_id=fake_leave_type.id,
        policy_id=fake_leave_policy.id,
        leave_type=fake_leave_type,
    )


@pytest.fixture
def fake_leave_request(
    fake_user: FakeUser,
    fake_leave_type: FakeLeaveType,
    fake_leave_policy: FakeLeavePolicy,
) -> FakeLeaveRequest:
    """Provide a fake leave request."""
    return FakeLeaveRequest(
        user_id=fake_user.id,
        leave_type_id=fake_leave_type.id,
        policy_id=fake_leave_policy.id,
    )


@pytest.fixture
def fake_workflow_step(
    fake_leave_request: FakeLeaveRequest, fake_manager: FakeUser
) -> FakeWorkflowStep:
    """Provide a fake workflow step."""
    return FakeWorkflowStep(
        leave_request_id=fake_leave_request.id,
        approver_id=fake_manager.id,
    )


# Repository fixtures
@pytest.fixture
def fake_user_repo() -> FakeUserRepository:
    """Provide a fake user repository."""
    return FakeUserRepository()


@pytest.fixture
def fake_leave_request_repo() -> FakeLeaveRequestRepository:
    """Provide a fake leave request repository."""
    return FakeLeaveRequestRepository()


@pytest.fixture
def fake_balance_repo() -> FakeLeaveBalanceRepository:
    """Provide a fake leave balance repository."""
    return FakeLeaveBalanceRepository()


@pytest.fixture
def fake_policy_repo() -> FakeLeavePolicyRepository:
    """Provide a fake leave policy repository."""
    return FakeLeavePolicyRepository()


@pytest.fixture
def fake_workflow_step_repo() -> FakeWorkflowStepRepository:
    """Provide a fake workflow step repository."""
    return FakeWorkflowStepRepository()


@pytest.fixture
def fake_audit_repo() -> FakeAuditRepository:
    """Provide a fake audit repository."""
    return FakeAuditRepository()


# ==============================================================================
# Integration Test Fixtures
# ==============================================================================


@pytest.fixture
def test_client() -> TestClient:
    """Provide a FastAPI test client.

    Uses the actual app with dependency overrides for testing.
    """
    from lms.app.main import app

    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Provide authorization headers with a fake token.

    Works with DEBUG mode auth stub.
    """
    return {"Authorization": "Bearer fake-test-token"}


@pytest.fixture
def admin_user_id() -> UUID:
    """Provide a fixed admin user ID for testing."""
    return UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def test_user_id() -> UUID:
    """Provide a fixed test user ID for testing."""
    return UUID("00000000-0000-0000-0000-000000000002")
