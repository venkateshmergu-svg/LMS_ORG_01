"""Unit tests for WorkflowEngine.

Tests:
- Workflow resolution
- Step instantiation
- Approval flow (approve/reject)
- State machine transitions
- Error cases
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from lms.app.core.enums import LeaveRequestStatus, WorkflowStepStatus
from lms.app.core.exceptions import (
    ApprovalException,
    WorkflowNotFoundException,
    WorkflowStateException,
)
from lms.app.engines.workflow_engine import (
    StepActivated,
    WorkflowCompleted,
    WorkflowEngine,
)
from lms.app.repositories import AuditContext
from tests.conftest import (
    FakeLeaveRequest,
    FakeUser,
    FakeWorkflowConfiguration,
    FakeWorkflowStep,
)


class FakeSession:
    """Fake SQLAlchemy session for workflow tests that handles execute()."""

    def __init__(self, step_repo=None) -> None:
        self.step_repo = step_repo
        self.is_active = True

    def execute(self, stmt):
        """Return a mock result with steps from the step_repo."""
        mock_result = MagicMock()
        if self.step_repo:
            # Get all steps sorted by step_order
            steps = sorted(
                list(self.step_repo._entities.values()),
                key=lambda s: getattr(s, "step_order", 0),
            )
            mock_result.scalars.return_value.all.return_value = steps
        else:
            mock_result.scalars.return_value.all.return_value = []
        return mock_result


class FakeWorkflowConfigurationRepository:
    """Fake workflow configuration repository."""

    def __init__(self) -> None:
        self._workflows: list = []

    def list_active_for_org(self, organization_id, on_datetime) -> list:
        return self._workflows


class FakeWorkflowStepRepository:
    """Fake workflow step repository."""

    def __init__(self) -> None:
        self._entities: dict = {}
        self._updates: list = []

    def get(self, entity_id):
        return self._entities.get(entity_id)

    def get_required(self, entity_id):
        entity = self.get(entity_id)
        if entity is None:
            from lms.app.core.exceptions import EntityNotFoundException

            raise EntityNotFoundException("WorkflowStep", entity_id)
        return entity

    def add(self, entity, *, ctx, description=None):
        if hasattr(entity, "id") and entity.id:
            self._entities[entity.id] = entity
        else:
            entity.id = uuid4()
            self._entities[entity.id] = entity
        return entity

    def update_fields(self, entity, fields, *, ctx, description=None):
        self._updates.append({"entity_id": entity.id, "fields": fields})
        for key, value in fields.items():
            setattr(entity, key, value)
        return entity

    def list_for_request(self, leave_request_id) -> list:
        return sorted(
            [
                step
                for step in self._entities.values()
                if hasattr(step, "leave_request_id")
                and step.leave_request_id == leave_request_id
            ],
            key=lambda s: s.step_order,
        )


class FakeDelegationRepository:
    """Fake delegation repository."""

    pass


class FakeLeaveRequestRepository:
    """Fake leave request repository for workflow engine tests."""

    def __init__(self) -> None:
        self._entities: dict = {}
        self._updates: list = []

    def get(self, entity_id):
        return self._entities.get(entity_id)

    def get_required(self, entity_id):
        entity = self.get(entity_id)
        if entity is None:
            from lms.app.core.exceptions import EntityNotFoundException

            raise EntityNotFoundException("LeaveRequest", entity_id)
        return entity

    def update_fields(self, entity, fields, *, ctx, description=None):
        self._updates.append({"entity_id": entity.id, "fields": fields})
        for key, value in fields.items():
            setattr(entity, key, value)
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


class FakeAuditRepository:
    """Fake audit repository."""

    def log(self, **kwargs):
        pass


@pytest.fixture
def workflow_repo() -> FakeWorkflowConfigurationRepository:
    return FakeWorkflowConfigurationRepository()


@pytest.fixture
def step_repo() -> FakeWorkflowStepRepository:
    return FakeWorkflowStepRepository()


@pytest.fixture
def leave_request_repo() -> FakeLeaveRequestRepository:
    return FakeLeaveRequestRepository()


@pytest.fixture
def user_repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def fake_session_with_steps(step_repo: FakeWorkflowStepRepository) -> FakeSession:
    """Provide a fake session with access to step_repo."""
    return FakeSession(step_repo=step_repo)


@pytest.fixture
def workflow_engine(
    fake_session_with_steps: FakeSession,
    workflow_repo: FakeWorkflowConfigurationRepository,
    step_repo: FakeWorkflowStepRepository,
    leave_request_repo: FakeLeaveRequestRepository,
    user_repo: FakeUserRepository,
) -> WorkflowEngine:
    """Provide a WorkflowEngine with fake repositories."""
    return WorkflowEngine(
        fake_session_with_steps,  # type: ignore[arg-type]
        workflow_repo=workflow_repo,  # type: ignore[arg-type]
        step_repo=step_repo,  # type: ignore[arg-type]
        delegation_repo=FakeDelegationRepository(),  # type: ignore[arg-type]
        user_repo=user_repo,  # type: ignore[arg-type]
        leave_request_repo=leave_request_repo,  # type: ignore[arg-type]
        audit_repo=FakeAuditRepository(),  # type: ignore[arg-type]
    )


@pytest.mark.unit
class TestWorkflowResolution:
    """Tests for workflow resolution."""

    def test_resolve_workflow_returns_active_workflow(
        self,
        workflow_engine: WorkflowEngine,
        workflow_repo: FakeWorkflowConfigurationRepository,
        fake_leave_request: FakeLeaveRequest,
    ) -> None:
        """Test that resolve_workflow returns an active workflow."""
        workflow = FakeWorkflowConfiguration(
            organization_id=uuid4(),
            name="Standard Approval",
        )
        workflow_repo._workflows = [workflow]

        resolution = workflow_engine.resolve_workflow(
            organization_id=workflow.organization_id,
            leave_request=fake_leave_request,  # type: ignore[arg-type]
        )

        assert resolution.workflow == workflow
        assert "active workflow" in resolution.reason.lower()

    def test_resolve_workflow_raises_when_no_workflow_found(
        self,
        workflow_engine: WorkflowEngine,
        fake_leave_request: FakeLeaveRequest,
    ) -> None:
        """Test that WorkflowNotFoundException is raised when no workflow exists."""
        with pytest.raises(WorkflowNotFoundException):
            workflow_engine.resolve_workflow(
                organization_id=uuid4(),
                leave_request=fake_leave_request,  # type: ignore[arg-type]
            )


@pytest.mark.unit
class TestStepInstantiation:
    """Tests for workflow step instantiation."""

    def test_instantiate_steps_creates_steps_in_order(
        self,
        workflow_engine: WorkflowEngine,
        step_repo: FakeWorkflowStepRepository,
        fake_leave_request: FakeLeaveRequest,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that instantiate_steps creates steps in order."""
        workflow = FakeWorkflowConfiguration()
        approver_ids = [uuid4(), uuid4(), uuid4()]

        steps = workflow_engine.instantiate_steps(
            leave_request=fake_leave_request,  # type: ignore[arg-type]
            workflow=workflow,  # type: ignore[arg-type]
            approver_ids_in_order=approver_ids,
            ctx=audit_ctx,
        )

        assert len(steps) == 3
        for idx, step in enumerate(steps):
            assert step.step_order == idx
            assert step.approver_id == approver_ids[idx]

    def test_instantiate_steps_marks_first_step_pending(
        self,
        workflow_engine: WorkflowEngine,
        step_repo: FakeWorkflowStepRepository,
        fake_leave_request: FakeLeaveRequest,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that first step is marked as PENDING."""
        workflow = FakeWorkflowConfiguration()
        approver_ids = [uuid4(), uuid4()]

        steps = workflow_engine.instantiate_steps(
            leave_request=fake_leave_request,  # type: ignore[arg-type]
            workflow=workflow,  # type: ignore[arg-type]
            approver_ids_in_order=approver_ids,
            ctx=audit_ctx,
        )

        assert steps[0].status == WorkflowStepStatus.PENDING

    def test_instantiate_steps_raises_when_no_approvers(
        self,
        workflow_engine: WorkflowEngine,
        fake_leave_request: FakeLeaveRequest,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that WorkflowStateException is raised when no approvers provided."""
        workflow = FakeWorkflowConfiguration()

        with pytest.raises(WorkflowStateException) as exc_info:
            workflow_engine.instantiate_steps(
                leave_request=fake_leave_request,  # type: ignore[arg-type]
                workflow=workflow,  # type: ignore[arg-type]
                approver_ids_in_order=[],
                ctx=audit_ctx,
            )

        assert "no approvers" in str(exc_info.value).lower()


@pytest.mark.unit
class TestApproval:
    """Tests for approval flow."""

    def test_approve_step_updates_status(
        self,
        workflow_engine: WorkflowEngine,
        step_repo: FakeWorkflowStepRepository,
        leave_request_repo: FakeLeaveRequestRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that approve updates step status to APPROVED."""
        approver_id = uuid4()
        leave_request = FakeLeaveRequest(status=LeaveRequestStatus.PENDING_APPROVAL)
        step = FakeWorkflowStep(
            leave_request_id=leave_request.id,
            approver_id=approver_id,
            status=WorkflowStepStatus.PENDING,
        )

        step_repo._entities[step.id] = step
        leave_request_repo._entities[leave_request.id] = leave_request

        result = workflow_engine.approve(
            step_id=step.id,
            actor_user_id=approver_id,
            comment="Approved",
            ctx=audit_ctx,
        )

        assert step.status == WorkflowStepStatus.APPROVED

    def test_approve_raises_when_not_assigned_approver(
        self,
        workflow_engine: WorkflowEngine,
        step_repo: FakeWorkflowStepRepository,
        leave_request_repo: FakeLeaveRequestRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that ApprovalException is raised when actor is not the assigned approver."""
        assigned_approver = uuid4()
        wrong_approver = uuid4()

        leave_request = FakeLeaveRequest(status=LeaveRequestStatus.PENDING_APPROVAL)
        step = FakeWorkflowStep(
            leave_request_id=leave_request.id,
            approver_id=assigned_approver,
            status=WorkflowStepStatus.PENDING,
        )

        step_repo._entities[step.id] = step
        leave_request_repo._entities[leave_request.id] = leave_request

        with pytest.raises(ApprovalException) as exc_info:
            workflow_engine.approve(
                step_id=step.id,
                actor_user_id=wrong_approver,
                ctx=audit_ctx,
            )

        assert "assigned approver" in str(exc_info.value).lower()

    def test_approve_raises_when_step_not_pending(
        self,
        workflow_engine: WorkflowEngine,
        step_repo: FakeWorkflowStepRepository,
        leave_request_repo: FakeLeaveRequestRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that WorkflowStateException is raised when step is not PENDING."""
        approver_id = uuid4()
        leave_request = FakeLeaveRequest(status=LeaveRequestStatus.PENDING_APPROVAL)
        step = FakeWorkflowStep(
            leave_request_id=leave_request.id,
            approver_id=approver_id,
            status=WorkflowStepStatus.APPROVED,  # Already approved
        )

        step_repo._entities[step.id] = step
        leave_request_repo._entities[leave_request.id] = leave_request

        with pytest.raises(WorkflowStateException) as exc_info:
            workflow_engine.approve(
                step_id=step.id,
                actor_user_id=approver_id,
                ctx=audit_ctx,
            )

        assert "expected pending" in str(exc_info.value).lower()

    def test_approve_raises_when_request_not_pending_approval(
        self,
        workflow_engine: WorkflowEngine,
        step_repo: FakeWorkflowStepRepository,
        leave_request_repo: FakeLeaveRequestRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that WorkflowStateException is raised when request is not in PENDING_APPROVAL."""
        approver_id = uuid4()
        leave_request = FakeLeaveRequest(
            status=LeaveRequestStatus.DRAFT
        )  # Not submitted
        step = FakeWorkflowStep(
            leave_request_id=leave_request.id,
            approver_id=approver_id,
            status=WorkflowStepStatus.PENDING,
        )

        step_repo._entities[step.id] = step
        leave_request_repo._entities[leave_request.id] = leave_request

        with pytest.raises(WorkflowStateException):
            workflow_engine.approve(
                step_id=step.id,
                actor_user_id=approver_id,
                ctx=audit_ctx,
            )


@pytest.mark.unit
class TestRejection:
    """Tests for rejection flow."""

    def test_reject_step_updates_status(
        self,
        workflow_engine: WorkflowEngine,
        step_repo: FakeWorkflowStepRepository,
        leave_request_repo: FakeLeaveRequestRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that reject updates step status to REJECTED."""
        approver_id = uuid4()
        leave_request = FakeLeaveRequest(status=LeaveRequestStatus.PENDING_APPROVAL)
        step = FakeWorkflowStep(
            leave_request_id=leave_request.id,
            approver_id=approver_id,
            status=WorkflowStepStatus.PENDING,
        )

        step_repo._entities[step.id] = step
        leave_request_repo._entities[leave_request.id] = leave_request

        result = workflow_engine.reject(
            step_id=step.id,
            actor_user_id=approver_id,
            comment="Not enough notice",
            ctx=audit_ctx,
        )

        assert step.status == WorkflowStepStatus.REJECTED

    def test_reject_raises_when_not_assigned_approver(
        self,
        workflow_engine: WorkflowEngine,
        step_repo: FakeWorkflowStepRepository,
        leave_request_repo: FakeLeaveRequestRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that ApprovalException is raised when actor is not the assigned approver."""
        assigned_approver = uuid4()
        wrong_approver = uuid4()

        leave_request = FakeLeaveRequest(status=LeaveRequestStatus.PENDING_APPROVAL)
        step = FakeWorkflowStep(
            leave_request_id=leave_request.id,
            approver_id=assigned_approver,
            status=WorkflowStepStatus.PENDING,
        )

        step_repo._entities[step.id] = step
        leave_request_repo._entities[leave_request.id] = leave_request

        with pytest.raises(ApprovalException):
            workflow_engine.reject(
                step_id=step.id,
                actor_user_id=wrong_approver,
                ctx=audit_ctx,
            )
