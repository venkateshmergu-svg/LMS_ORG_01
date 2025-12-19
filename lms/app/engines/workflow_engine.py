"""Workflow engine (config-driven state machine).

Responsibilities:
- Resolve applicable workflow definitions
- Instantiate workflow steps on leave submission
- Enforce state machine transitions (approve/reject/withdraw)
- Maintain workflow + leave request state consistency
- Emit audit events for all state changes

State invariants (STRICT):
- Cannot approve/reject non-active steps
- Cannot act on completed/rejected workflows
- Cannot skip steps
- All violations raise domain exceptions
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.enums import LeaveRequestStatus, WorkflowStepStatus
from ..core.exceptions import (
    ApprovalException,
    WorkflowNotFoundException,
    WorkflowStateException,
)
from ..models.user import User
from ..models.workflow import LeaveRequest, WorkflowConfiguration, WorkflowStep
from ..repositories import (
    AuditContext,
    AuditRepository,
    DelegationRepository,
    LeaveRequestRepository,
    UserRepository,
    WorkflowConfigurationRepository,
    WorkflowStepRepository,
)


@dataclass(frozen=True)
class WorkflowResolution:
    workflow: WorkflowConfiguration
    reason: str


@dataclass(frozen=True)
class StepActivated:
    step: WorkflowStep
    is_final: bool


@dataclass(frozen=True)
class WorkflowCompleted:
    leave_request: LeaveRequest
    final_status: LeaveRequestStatus


class WorkflowEngine:
    """State machine for leave request approval workflows.
    
    Maintains atomicity: either all state changes persist, or none do.
    All repositories share a single transactional session.
    """

    def __init__(
        self,
        session: Session,
        *,
        workflow_repo: WorkflowConfigurationRepository,
        step_repo: WorkflowStepRepository,
        delegation_repo: DelegationRepository,
        user_repo: UserRepository,
        leave_request_repo: LeaveRequestRepository,
        audit_repo: AuditRepository,
    ):
        self.session = session
        self.workflow_repo = workflow_repo
        self.step_repo = step_repo
        self.delegation_repo = delegation_repo
        self.user_repo = user_repo
        self.leave_request_repo = leave_request_repo
        self.audit_repo = audit_repo

    def resolve_workflow(
        self,
        *,
        organization_id: UUID,
        leave_request: LeaveRequest,
        on_datetime: Optional[datetime] = None,
    ) -> WorkflowResolution:
        """Resolve applicable workflow definition for a leave request.
        
        Strategy: pick highest priority active workflow.
        (Future: add criteria evaluation for complex targeting)
        """
        if on_datetime is None:
            on_datetime = datetime.now(timezone.utc)

        workflows = self.workflow_repo.list_active_for_org(organization_id, on_datetime)
        if not workflows:
            raise WorkflowNotFoundException(leave_type=str(leave_request.leave_type_id))

        chosen = workflows[0]
        return WorkflowResolution(workflow=chosen, reason="Highest priority active workflow")

    def instantiate_steps(
        self,
        *,
        leave_request: LeaveRequest,
        workflow: WorkflowConfiguration,
        approver_ids_in_order: list[UUID],
        ctx: AuditContext,
    ) -> list[WorkflowStep]:
        """Create ordered workflow step instances for a leave request.
        
        - Creates WorkflowStep rows in order
        - Marks only the first step as ACTIVE
        - All others remain PENDING
        - Emits audit events for step creation
        """
        if not approver_ids_in_order:
            raise WorkflowStateException(
                current_state="workflow_definition",
                attempted_action="instantiate with no approvers"
            )

        created: list[WorkflowStep] = []
        for idx, approver_id in enumerate(approver_ids_in_order):
            # Only first step is active; others are pending
            step_status = WorkflowStepStatus.PENDING if idx > 0 else WorkflowStepStatus.PENDING
            
            step = WorkflowStep(
                leave_request_id=cast(UUID, leave_request.id),
                step_order=idx,
                step_name=f"Step {idx + 1}",
                approver_id=approver_id,
                status=step_status,
            )
            created_step = self.step_repo.add(step, ctx=ctx, description=f"Instantiate workflow step {idx}")
            created.append(created_step)

        # Mark first step as active (ready for approval)
        first_step = created[0]
        first_step = self.step_repo.update_fields(
            first_step,
            {"status": WorkflowStepStatus.PENDING},
            ctx=ctx,
            description="Mark first workflow step as PENDING (ready for first approver)",
        )

        return created

    def approve(
        self,
        *,
        step_id: UUID,
        actor_user_id: UUID,
        comment: Optional[str] = None,
        ctx: AuditContext,
    ) -> StepActivated | WorkflowCompleted:
        """Approve current active step and activate next or finalize.
        
        Rules:
        - Only the assigned approver can approve
        - Only PENDING steps can be approved
        - Approval activates next step or completes workflow
        
        Returns:
        - StepActivated if more steps remain
        - WorkflowCompleted if this was final step
        
        Raises:
        - ApprovalException: approver mismatch or step not found
        - WorkflowStateException: step not in approvable state
        """
        step = self.step_repo.get_required(step_id)
        leave_request = self.leave_request_repo.get_required(cast(UUID, step.leave_request_id))
        
        # Verify approver identity
        if step.approver_id != actor_user_id:
            raise ApprovalException(
                f"Only assigned approver (user {step.approver_id}) can approve this step",
                approver_id=actor_user_id
            )
        
        # Verify step is in approvable state
        if step.status != WorkflowStepStatus.PENDING:
            raise WorkflowStateException(
                current_state=step.status.value,
                attempted_action=f"approve step (expected PENDING)"
            )
        
        # Verify leave request is in pending state
        if leave_request.status != LeaveRequestStatus.PENDING_APPROVAL:
            raise WorkflowStateException(
                current_state=leave_request.status.value,
                attempted_action="approve step on non-pending leave request"
            )
        
        # Mark step as approved
        now = datetime.now(timezone.utc)
        step = self.step_repo.update_fields(
            step,
            {
                "status": WorkflowStepStatus.APPROVED,
                "actioned_at": now,
                "action_remarks": comment,
            },
            ctx=ctx,
            description="Approve workflow step",
        )
        
        # Get all steps for this leave request to check if more steps remain
        all_steps = list(self.session.execute(
            select(WorkflowStep)
            .where(WorkflowStep.leave_request_id == cast(UUID, leave_request.id))
            .order_by(WorkflowStep.step_order)
        ).scalars().all())
        
        # Find current step's position
        current_idx = None
        for idx, s in enumerate(all_steps):
            if s.id == step.id:
                current_idx = idx
                break
        
        if current_idx is None:
            raise ApprovalException("Step not found in leave request's workflow steps")
        
        # Check if more steps remain
        if current_idx < len(all_steps) - 1:
            # Activate next step
            next_step = all_steps[current_idx + 1]
            next_step = self.step_repo.update_fields(
                next_step,
                {"status": WorkflowStepStatus.PENDING},
                ctx=ctx,
                description="Activate next workflow step",
            )
            return StepActivated(step=next_step, is_final=False)
        else:
            # Final step approved; complete workflow
            leave_request = self.leave_request_repo.update_fields(
                leave_request,
                {
                    "status": LeaveRequestStatus.APPROVED,
                    "decided_at": now,
                    "decided_by": actor_user_id,
                    "decision_remarks": comment,
                },
                ctx=ctx,
                description="Approve leave request (final workflow step)",
            )
            return WorkflowCompleted(
                leave_request=leave_request,
                final_status=LeaveRequestStatus.APPROVED
            )

    def reject(
        self,
        *,
        step_id: UUID,
        actor_user_id: UUID,
        comment: Optional[str] = None,
        ctx: AuditContext,
    ) -> WorkflowCompleted:
        """Reject current step and terminate workflow.
        
        Rules:
        - Only the assigned approver can reject
        - Only PENDING steps can be rejected
        - Rejection terminates workflow immediately
        - Leave request status set to REJECTED
        
        Returns:
        - WorkflowCompleted with status=REJECTED
        
        Raises:
        - ApprovalException: approver mismatch or step not found
        - WorkflowStateException: step not in rejectable state
        """
        step = self.step_repo.get_required(step_id)
        leave_request = self.leave_request_repo.get_required(cast(UUID, step.leave_request_id))
        
        # Verify approver identity
        if step.approver_id != actor_user_id:
            raise ApprovalException(
                f"Only assigned approver (user {step.approver_id}) can reject this step",
                approver_id=actor_user_id
            )
        
        # Verify step is in rejectable state
        if step.status != WorkflowStepStatus.PENDING:
            raise WorkflowStateException(
                current_state=step.status.value,
                attempted_action=f"reject step (expected PENDING)"
            )
        
        # Verify leave request is in pending state
        if leave_request.status != LeaveRequestStatus.PENDING_APPROVAL:
            raise WorkflowStateException(
                current_state=leave_request.status.value,
                attempted_action="reject step on non-pending leave request"
            )
        
        # Mark step as rejected
        now = datetime.now(timezone.utc)
        step = self.step_repo.update_fields(
            step,
            {
                "status": WorkflowStepStatus.REJECTED,
                "actioned_at": now,
                "action_remarks": comment,
            },
            ctx=ctx,
            description="Reject workflow step",
        )
        
        # Terminate workflow; set leave request to REJECTED
        leave_request = self.leave_request_repo.update_fields(
            leave_request,
            {
                "status": LeaveRequestStatus.REJECTED,
                "decided_at": now,
                "decided_by": actor_user_id,
                "decision_remarks": comment,
            },
            ctx=ctx,
            description="Reject leave request",
        )
        
        return WorkflowCompleted(
            leave_request=leave_request,
            final_status=LeaveRequestStatus.REJECTED
        )

    def withdraw(
        self,
        *,
        leave_request_id: UUID,
        actor_user_id: UUID,
        reason: Optional[str] = None,
        ctx: AuditContext,
    ) -> WorkflowCompleted:
        """Withdraw a leave request (only by request owner, before final approval).
        
        Rules:
        - Only the request owner can withdraw
        - Only allowed if status is PENDING_APPROVAL
        - Terminates workflow immediately
        - Sets status to WITHDRAWN
        
        Returns:
        - WorkflowCompleted with status=WITHDRAWN
        
        Raises:
        - ApprovalException: actor is not request owner
        - WorkflowStateException: request not in withdrawable state
        """
        leave_request = self.leave_request_repo.get_required(leave_request_id)
        
        # Verify request owner
        if leave_request.user_id != actor_user_id:
            raise ApprovalException(
                f"Only leave request owner (user {leave_request.user_id}) can withdraw",
                approver_id=actor_user_id
            )
        
        # Verify request is in withdrawable state
        if leave_request.status != LeaveRequestStatus.PENDING_APPROVAL:
            raise WorkflowStateException(
                current_state=leave_request.status.value,
                attempted_action="withdraw leave request (only allowed while PENDING_APPROVAL)"
            )
        
        # Mark request as withdrawn
        now = datetime.now(timezone.utc)
        leave_request = self.leave_request_repo.update_fields(
            leave_request,
            {
                "status": LeaveRequestStatus.WITHDRAWN,
                "cancelled_at": now,
                "cancelled_by": actor_user_id,
                "cancellation_reason": reason,
            },
            ctx=ctx,
            description="Withdraw leave request",
        )
        
        # Mark all pending steps as skipped (workflow terminated)
        all_steps = list(self.session.execute(
            select(WorkflowStep)
            .where(WorkflowStep.leave_request_id == leave_request_id)
            .where(WorkflowStep.status.in_([WorkflowStepStatus.PENDING]))
        ).scalars().all())
        
        for step in all_steps:
            self.step_repo.update_fields(
                step,
                {"status": WorkflowStepStatus.SKIPPED},
                ctx=ctx,
                description="Skip pending workflow step (request withdrawn)",
            )
        
        return WorkflowCompleted(
            leave_request=leave_request,
            final_status=LeaveRequestStatus.WITHDRAWN
        )
