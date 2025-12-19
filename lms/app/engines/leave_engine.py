"""Leave engine (orchestration).

Responsibilities:
- Orchestrate leave request lifecycle
- Delegate policy rules to PolicyEngine
- Delegate workflow state machine to WorkflowEngine
- Persist all mutations through repositories (no direct DB access)

Controllers MUST call engines; controllers contain no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Optional, cast
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from ..core.enums import LeaveRequestStatus
from ..core.exceptions import LeaveOverlapException, WorkflowNotFoundException
from ..models.user import User
from ..models.workflow import LeaveRequest, LeaveRequestComment, LeaveRequestDate
from ..repositories import (
    AuditContext,
    AuditRepository,
    LeaveRequestCommentRepository,
    LeaveRequestDateRepository,
    LeaveRequestRepository,
    LeaveTypeRepository,
    UserRepository,
)
from .policy_engine import PolicyEngine
from .workflow_engine import WorkflowEngine


@dataclass(frozen=True)
class LeaveRequestCreated:
    leave_request: LeaveRequest


class LeaveEngine:
    def __init__(
        self,
        session: Session,
        *,
        user_repo: UserRepository,
        leave_type_repo: LeaveTypeRepository,
        request_repo: LeaveRequestRepository,
        request_date_repo: LeaveRequestDateRepository,
        request_comment_repo: LeaveRequestCommentRepository,
        policy_engine: PolicyEngine,
        workflow_engine: WorkflowEngine,
    ):
        self.session = session
        self.user_repo = user_repo
        self.leave_type_repo = leave_type_repo
        self.request_repo = request_repo
        self.request_date_repo = request_date_repo
        self.request_comment_repo = request_comment_repo
        self.policy_engine = policy_engine
        self.workflow_engine = workflow_engine

    def create_leave_request(
        self,
        *,
        user_id: UUID,
        leave_type_id: UUID,
        start_date: date,
        end_date: date,
        total_days: float,
        reason: Optional[str],
        ctx: AuditContext,
    ) -> LeaveRequestCreated:
        # Basic overlap check (generic correctness, not a business rule).
        overlaps = self.request_repo.find_overlaps(user_id, start_date, end_date)
        if overlaps:
            raise LeaveOverlapException([{"request_id": str(r.id)} for r in overlaps])

        user = self.user_repo.get_required(user_id)
        leave_type = self.leave_type_repo.get_required(leave_type_id)

        # Resolve policy and eligibility via PolicyEngine.
        leave_type_pk = cast(UUID, leave_type.id)
        resolution = self.policy_engine.resolve_policy_for_user(user=user, leave_type_id=leave_type_pk)
        self.policy_engine.assert_eligible(user=user, policy=resolution.policy)

        req = LeaveRequest(
            request_number=f"LR-{uuid4().hex[:12].upper()}",
            user_id=cast(UUID, user.id),
            leave_type_id=leave_type_pk,
            policy_id=cast(UUID, resolution.policy.id),
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            reason=reason,
            status=LeaveRequestStatus.DRAFT,
        )
        req = self.request_repo.add(req, ctx=ctx, description="Create leave request")

        # Persist per-day rows (simple contiguous expansion for skeleton).
        cur = start_date
        while cur <= end_date:
            day = LeaveRequestDate(leave_request_id=req.id, leave_date=cur, day_value=1.0)
            self.request_date_repo.add(day, ctx=ctx, description="Add leave request day")
            cur = date.fromordinal(cur.toordinal() + 1)

        return LeaveRequestCreated(leave_request=req)

    def submit(self, *, request_id: UUID, ctx: AuditContext) -> LeaveRequest:
        """Submit a leave request and instantiate its workflow.
        
        Actions:
        1. Verify request is in DRAFT status
        2. Resolve applicable workflow definition
        3. Determine approvers (for now: request owner's manager chain)
        4. Instantiate workflow steps
        5. Transition request to PENDING_APPROVAL
        
        Returns:
        - Updated LeaveRequest with status=PENDING_APPROVAL
        
        Raises:
        - LeaveRequestNotFoundException: request not found
        - WorkflowStateException: request not in DRAFT status
        - WorkflowNotFoundException: no applicable workflow defined
        """
        req = self.request_repo.get_required(request_id)
        
        # Verify request is in DRAFT status
        if req.status != LeaveRequestStatus.DRAFT:
            from ..core.exceptions import WorkflowStateException
            raise WorkflowStateException(
                current_state=req.status.value,
                attempted_action="submit (only DRAFT requests can be submitted)"
            )
        
        # Get user and organization context
        user = self.user_repo.get_required(cast(UUID, req.user_id))
        organization_id = cast(UUID, user.organization_id)
        
        # Resolve workflow for this leave type
        workflow_resolution = self.workflow_engine.resolve_workflow(
            organization_id=organization_id,
            leave_request=req,
        )
        
        # Determine approvers: start with user's manager
        # (In production, this would query a complex chain or policy rules)
        approver_ids: list[UUID] = []
        if user.manager_id:
            approver_ids.append(cast(UUID, user.manager_id))
        
        if not approver_ids:
            raise WorkflowNotFoundException(
                leave_type=str(req.leave_type_id)
            )
        
        # Instantiate workflow steps (creates step rows, marks first as PENDING)
        steps = self.workflow_engine.instantiate_steps(
            leave_request=req,
            workflow=workflow_resolution.workflow,
            approver_ids_in_order=approver_ids,
            ctx=ctx,
        )
        
        # Transition leave request to PENDING_APPROVAL
        now = datetime.now(timezone.utc)
        updated = self.request_repo.update_fields(
            req,
            {
                "status": LeaveRequestStatus.PENDING_APPROVAL,
                "submitted_at": now,
            },
            ctx=ctx,
            description="Submit leave request (workflow instantiated)",
        )
        
        return updated

    def add_comment(self, *, request_id: UUID, user_id: UUID, comment: str, is_internal: bool, ctx: AuditContext) -> LeaveRequestComment:
        c = LeaveRequestComment(
            leave_request_id=request_id,
            user_id=user_id,
            comment=comment,
            is_internal=is_internal,
        )
        return self.request_comment_repo.add(c, ctx=ctx, description="Add leave request comment")

    def approve_step(
        self,
        *,
        step_id: UUID,
        actor_user_id: UUID,
        comment: Optional[str],
        ctx: AuditContext,
    ) -> dict:
        """Approve a workflow step.
        
        Delegates to WorkflowEngine for state machine logic.
        Returns dict with leave_request, is_final, status.
        """
        from .workflow_engine import StepActivated, WorkflowCompleted
        result = self.workflow_engine.approve(
            step_id=step_id,
            actor_user_id=actor_user_id,
            comment=comment,
            ctx=ctx,
        )
        
        # Unwrap result union type
        if isinstance(result, WorkflowCompleted):
            return {
                "leave_request": result.leave_request,
                "is_final": True,
                "status": result.final_status,
            }
        else:
            # StepActivated
            return {
                "leave_request": self.request_repo.get_required(cast(UUID, result.step.leave_request_id)),
                "is_final": result.is_final,
                "status": LeaveRequestStatus.PENDING_APPROVAL,
            }

    def reject_step(
        self,
        *,
        step_id: UUID,
        actor_user_id: UUID,
        comment: Optional[str],
        ctx: AuditContext,
    ) -> dict:
        """Reject a workflow step.
        
        Delegates to WorkflowEngine for state machine logic.
        Returns dict with leave_request, is_final, status.
        """
        result = self.workflow_engine.reject(
            step_id=step_id,
            actor_user_id=actor_user_id,
            comment=comment,
            ctx=ctx,
        )
        
        return {
            "leave_request": result.leave_request,
            "is_final": True,
            "status": result.final_status,
        }

    def withdraw_request(
        self,
        *,
        leave_request_id: UUID,
        actor_user_id: UUID,
        reason: Optional[str],
        ctx: AuditContext,
    ) -> dict:
        """Withdraw a leave request.
        
        Delegates to WorkflowEngine for state machine logic.
        Returns dict with leave_request, is_final, status.
        """
        result = self.workflow_engine.withdraw(
            leave_request_id=leave_request_id,
            actor_user_id=actor_user_id,
            reason=reason,
            ctx=ctx,
        )
        
        return {
            "leave_request": result.leave_request,
            "is_final": True,
            "status": result.final_status,
        }
