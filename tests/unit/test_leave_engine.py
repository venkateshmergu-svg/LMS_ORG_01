"""Unit tests for LeaveEngine.

Tests:
- Leave request creation
- Leave request submission
- Comment addition
- Approval/rejection delegation
- Error handling
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from lms.app.core.enums import LeaveRequestStatus
from lms.app.core.exceptions import (
    LeaveOverlapException,
    WorkflowNotFoundException,
    WorkflowStateException,
)
from lms.app.engines.leave_engine import LeaveEngine, LeaveRequestCreated
from lms.app.repositories import AuditContext
from tests.conftest import (
    FakeLeavePolicy,
    FakeLeaveRequest,
    FakeLeaveType,
    FakeSession,
    FakeUser,
    FakeWorkflowConfiguration,
)


class FakeLeaveTypeRepository:
    """Fake leave type repository."""

    def __init__(self) -> None:
        self._entities: dict = {}

    def get_required(self, entity_id):
        entity = self._entities.get(entity_id)
        if entity is None:
            from lms.app.core.exceptions import EntityNotFoundException

            raise EntityNotFoundException("LeaveType", entity_id)
        return entity


class FakeUserRepository:
    """Fake user repository."""

    def __init__(self) -> None:
        self._entities: dict = {}

    def get_required(self, entity_id):
        entity = self._entities.get(entity_id)
        if entity is None:
            from lms.app.core.exceptions import EntityNotFoundException

            raise EntityNotFoundException("User", entity_id)
        return entity


class FakeLeaveRequestRepository:
    """Fake leave request repository."""

    def __init__(self) -> None:
        self._entities: dict = {}
        self._overlaps: list = []
        self._updates: list = []

    def find_overlaps(self, user_id, start_date, end_date) -> list:
        return self._overlaps

    def get_required(self, entity_id):
        entity = self._entities.get(entity_id)
        if entity is None:
            from lms.app.core.exceptions import EntityNotFoundException

            raise EntityNotFoundException("LeaveRequest", entity_id)
        return entity

    def add(self, entity, *, ctx, description=None):
        if not hasattr(entity, "id") or entity.id is None:
            entity.id = uuid4()
        self._entities[entity.id] = entity
        return entity

    def update_fields(self, entity, fields, *, ctx, description=None):
        self._updates.append({"entity_id": entity.id, "fields": fields})
        for key, value in fields.items():
            setattr(entity, key, value)
        return entity


class FakeLeaveRequestDateRepository:
    """Fake leave request date repository."""

    def __init__(self) -> None:
        self._entities: list = []

    def add(self, entity, *, ctx, description=None):
        self._entities.append(entity)
        return entity


class FakeLeaveRequestCommentRepository:
    """Fake leave request comment repository."""

    def __init__(self) -> None:
        self._entities: list = []

    def add(self, entity, *, ctx, description=None):
        entity.id = uuid4()
        self._entities.append(entity)
        return entity


class FakePolicyEngine:
    """Fake policy engine."""

    def __init__(self) -> None:
        self.resolved_policy: FakeLeavePolicy | None = None
        self.eligibility_error: Exception | None = None

    def resolve_policy_for_user(self, *, user, leave_type_id, on_datetime=None):
        if self.resolved_policy:
            from dataclasses import dataclass

            @dataclass(frozen=True)
            class PolicyResolution:
                policy: FakeLeavePolicy
                reason: str

            return PolicyResolution(policy=self.resolved_policy, reason="Test policy")
        from lms.app.core.exceptions import PolicyNotFoundException

        raise PolicyNotFoundException(leave_type_id)

    def assert_eligible(self, *, user, policy, on_datetime=None):
        if self.eligibility_error:
            raise self.eligibility_error


class FakeWorkflowEngine:
    """Fake workflow engine."""

    def __init__(self) -> None:
        self.resolved_workflow: FakeWorkflowConfiguration | None = None
        self.instantiated_steps: list = []
        self.approve_result = None
        self.reject_result = None

    def resolve_workflow(self, *, organization_id, leave_request, on_datetime=None):
        if self.resolved_workflow:
            from dataclasses import dataclass

            @dataclass(frozen=True)
            class WorkflowResolution:
                workflow: FakeWorkflowConfiguration
                reason: str

            return WorkflowResolution(
                workflow=self.resolved_workflow, reason="Test workflow"
            )
        from lms.app.core.exceptions import WorkflowNotFoundException

        raise WorkflowNotFoundException()

    def instantiate_steps(self, *, leave_request, workflow, approver_ids_in_order, ctx):
        self.instantiated_steps = approver_ids_in_order
        return []

    def approve(self, *, step_id, actor_user_id, comment, ctx):
        return self.approve_result

    def reject(self, *, step_id, actor_user_id, comment, ctx):
        return self.reject_result


@pytest.fixture
def user_repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def leave_type_repo() -> FakeLeaveTypeRepository:
    return FakeLeaveTypeRepository()


@pytest.fixture
def request_repo() -> FakeLeaveRequestRepository:
    return FakeLeaveRequestRepository()


@pytest.fixture
def request_date_repo() -> FakeLeaveRequestDateRepository:
    return FakeLeaveRequestDateRepository()


@pytest.fixture
def comment_repo() -> FakeLeaveRequestCommentRepository:
    return FakeLeaveRequestCommentRepository()


@pytest.fixture
def policy_engine() -> FakePolicyEngine:
    return FakePolicyEngine()


@pytest.fixture
def workflow_engine() -> FakeWorkflowEngine:
    return FakeWorkflowEngine()


@pytest.fixture
def leave_engine(
    fake_session: FakeSession,
    user_repo: FakeUserRepository,
    leave_type_repo: FakeLeaveTypeRepository,
    request_repo: FakeLeaveRequestRepository,
    request_date_repo: FakeLeaveRequestDateRepository,
    comment_repo: FakeLeaveRequestCommentRepository,
    policy_engine: FakePolicyEngine,
    workflow_engine: FakeWorkflowEngine,
) -> LeaveEngine:
    """Provide a LeaveEngine with fake repositories."""
    return LeaveEngine(
        fake_session,  # type: ignore[arg-type]
        user_repo=user_repo,  # type: ignore[arg-type]
        leave_type_repo=leave_type_repo,  # type: ignore[arg-type]
        request_repo=request_repo,  # type: ignore[arg-type]
        request_date_repo=request_date_repo,  # type: ignore[arg-type]
        request_comment_repo=comment_repo,  # type: ignore[arg-type]
        policy_engine=policy_engine,  # type: ignore[arg-type]
        workflow_engine=workflow_engine,  # type: ignore[arg-type]
    )


@pytest.mark.unit
class TestLeaveRequestCreation:
    """Tests for leave request creation."""

    def test_create_leave_request_success(
        self,
        leave_engine: LeaveEngine,
        user_repo: FakeUserRepository,
        leave_type_repo: FakeLeaveTypeRepository,
        policy_engine: FakePolicyEngine,
        request_date_repo: FakeLeaveRequestDateRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test successful leave request creation."""
        user = FakeUser(
            organization_id=uuid4(),
            hire_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )
        leave_type = FakeLeaveType(organization_id=user.organization_id)
        policy = FakeLeavePolicy(
            organization_id=user.organization_id,
            leave_type_id=leave_type.id,
        )

        user_repo._entities[user.id] = user
        leave_type_repo._entities[leave_type.id] = leave_type
        policy_engine.resolved_policy = policy

        result = leave_engine.create_leave_request(
            user_id=user.id,
            leave_type_id=leave_type.id,
            start_date=date(2024, 2, 1),
            end_date=date(2024, 2, 3),
            total_days=3.0,
            reason="Vacation",
            ctx=audit_ctx,
        )

        assert isinstance(result, LeaveRequestCreated)
        assert result.leave_request.status == LeaveRequestStatus.DRAFT
        assert result.leave_request.total_days == 3.0
        # Should create date records for each day
        assert len(request_date_repo._entities) == 3

    def test_create_leave_request_detects_overlap(
        self,
        leave_engine: LeaveEngine,
        user_repo: FakeUserRepository,
        leave_type_repo: FakeLeaveTypeRepository,
        request_repo: FakeLeaveRequestRepository,
        policy_engine: FakePolicyEngine,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that overlapping leave requests are detected."""
        user = FakeUser()
        leave_type = FakeLeaveType()

        user_repo._entities[user.id] = user
        leave_type_repo._entities[leave_type.id] = leave_type

        # Add an overlapping request
        existing_request = FakeLeaveRequest(
            user_id=user.id,
            start_date=date(2024, 2, 1),
            end_date=date(2024, 2, 5),
        )
        request_repo._overlaps = [existing_request]

        with pytest.raises(LeaveOverlapException):
            leave_engine.create_leave_request(
                user_id=user.id,
                leave_type_id=leave_type.id,
                start_date=date(2024, 2, 3),
                end_date=date(2024, 2, 7),
                total_days=5.0,
                reason="Vacation",
                ctx=audit_ctx,
            )


@pytest.mark.unit
class TestLeaveRequestSubmission:
    """Tests for leave request submission."""

    def test_submit_transitions_to_pending_approval(
        self,
        leave_engine: LeaveEngine,
        user_repo: FakeUserRepository,
        request_repo: FakeLeaveRequestRepository,
        workflow_engine: FakeWorkflowEngine,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that submit transitions request to PENDING_APPROVAL."""
        manager = FakeUser(role="manager")
        user = FakeUser(manager_id=manager.id)
        request = FakeLeaveRequest(
            user_id=user.id,
            status=LeaveRequestStatus.DRAFT,
        )
        workflow = FakeWorkflowConfiguration(organization_id=user.organization_id)

        user_repo._entities[user.id] = user
        user_repo._entities[manager.id] = manager
        request_repo._entities[request.id] = request
        workflow_engine.resolved_workflow = workflow

        result = leave_engine.submit(request_id=request.id, ctx=audit_ctx)

        assert result.status == LeaveRequestStatus.PENDING_APPROVAL
        assert result.submitted_at is not None

    def test_submit_raises_when_not_draft(
        self,
        leave_engine: LeaveEngine,
        request_repo: FakeLeaveRequestRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that submit raises WorkflowStateException when not in DRAFT."""
        request = FakeLeaveRequest(status=LeaveRequestStatus.APPROVED)
        request_repo._entities[request.id] = request

        with pytest.raises(WorkflowStateException) as exc_info:
            leave_engine.submit(request_id=request.id, ctx=audit_ctx)

        assert "draft" in str(exc_info.value).lower()

    def test_submit_raises_when_no_manager(
        self,
        leave_engine: LeaveEngine,
        user_repo: FakeUserRepository,
        request_repo: FakeLeaveRequestRepository,
        workflow_engine: FakeWorkflowEngine,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that submit raises WorkflowNotFoundException when user has no manager."""
        user = FakeUser(manager_id=None)  # No manager
        request = FakeLeaveRequest(
            user_id=user.id,
            status=LeaveRequestStatus.DRAFT,
        )
        workflow = FakeWorkflowConfiguration(organization_id=user.organization_id)

        user_repo._entities[user.id] = user
        request_repo._entities[request.id] = request
        workflow_engine.resolved_workflow = workflow

        with pytest.raises(WorkflowNotFoundException):
            leave_engine.submit(request_id=request.id, ctx=audit_ctx)


@pytest.mark.unit
class TestCommentAddition:
    """Tests for comment addition."""

    def test_add_comment_creates_comment(
        self,
        leave_engine: LeaveEngine,
        comment_repo: FakeLeaveRequestCommentRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that add_comment creates a comment."""
        request_id = uuid4()
        user_id = uuid4()

        comment = leave_engine.add_comment(
            request_id=request_id,
            user_id=user_id,
            comment="This is a test comment",
            is_internal=False,
            ctx=audit_ctx,
        )

        assert comment.comment == "This is a test comment"
        assert comment.is_internal is False
        assert len(comment_repo._entities) == 1

    def test_add_internal_comment(
        self,
        leave_engine: LeaveEngine,
        comment_repo: FakeLeaveRequestCommentRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that internal comments are marked correctly."""
        request_id = uuid4()
        user_id = uuid4()

        comment = leave_engine.add_comment(
            request_id=request_id,
            user_id=user_id,
            comment="Internal HR note",
            is_internal=True,
            ctx=audit_ctx,
        )

        assert comment.is_internal is True


@pytest.mark.unit
class TestApprovalDelegation:
    """Tests for approval/rejection delegation to WorkflowEngine."""

    def test_approve_step_delegates_to_workflow_engine(
        self,
        leave_engine: LeaveEngine,
        workflow_engine: FakeWorkflowEngine,
        request_repo: FakeLeaveRequestRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that approve_step delegates to WorkflowEngine."""
        from lms.app.engines.workflow_engine import WorkflowCompleted

        request = FakeLeaveRequest(status=LeaveRequestStatus.APPROVED)
        request_repo._entities[request.id] = request

        workflow_engine.approve_result = WorkflowCompleted(
            leave_request=request,  # type: ignore[arg-type]
            final_status=LeaveRequestStatus.APPROVED,
        )

        result = leave_engine.approve_step(
            step_id=uuid4(),
            actor_user_id=uuid4(),
            comment="Approved",
            ctx=audit_ctx,
        )

        assert result["is_final"] is True
        assert result["status"] == LeaveRequestStatus.APPROVED

    def test_reject_step_delegates_to_workflow_engine(
        self,
        leave_engine: LeaveEngine,
        workflow_engine: FakeWorkflowEngine,
        request_repo: FakeLeaveRequestRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that reject_step delegates to WorkflowEngine."""
        from lms.app.engines.workflow_engine import WorkflowCompleted

        request = FakeLeaveRequest(status=LeaveRequestStatus.REJECTED)
        request_repo._entities[request.id] = request

        workflow_engine.reject_result = WorkflowCompleted(
            leave_request=request,  # type: ignore[arg-type]
            final_status=LeaveRequestStatus.REJECTED,
        )

        result = leave_engine.reject_step(
            step_id=uuid4(),
            actor_user_id=uuid4(),
            comment="Not enough notice",
            ctx=audit_ctx,
        )

        assert result["status"] == LeaveRequestStatus.REJECTED
