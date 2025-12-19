"""Leave request endpoints.

Controllers contain no business logic; they call engines.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from ....engines import LeaveEngine
from ....repositories import AuditContext
from ....schemas.leave import (
    ApprovalAction,
    ApprovalResponse,
    LeaveRequestCommentCreate,
    LeaveRequestCreate,
    LeaveRequestResponse,
    SubmitResponse,
    WithdrawalRequest,
)
from ...deps import get_audit_context, get_leave_engine

router = APIRouter()


@router.post("", response_model=LeaveRequestResponse)
def create_leave_request(
    payload: LeaveRequestCreate,
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    result = engine.create_leave_request(
        user_id=payload.user_id,
        leave_type_id=payload.leave_type_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        total_days=payload.total_days,
        reason=payload.reason,
        ctx=ctx,
    )
    return result.leave_request


@router.post("/{request_id}/submit", response_model=SubmitResponse)
def submit_leave_request(
    request_id: UUID,
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    updated = engine.submit(request_id=request_id, ctx=ctx)
    return SubmitResponse.model_validate(updated)


@router.post("/{request_id}/comments", response_model=dict)
def add_comment(
    request_id: UUID,
    payload: LeaveRequestCommentCreate,
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    comment = engine.add_comment(
        request_id=request_id,
        user_id=payload.user_id,
        comment=payload.comment,
        is_internal=payload.is_internal,
        ctx=ctx,
    )
    return {"id": str(comment.id)}


@router.post("/steps/{step_id}/approve", response_model=ApprovalResponse)
def approve_step(
    step_id: UUID,
    payload: ApprovalAction,
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    """Approve a workflow step.
    
    Only the assigned approver can approve.
    Activates next step or finalizes workflow.
    """
    result = engine.approve_step(
        step_id=step_id,
        actor_user_id=payload.actor_user_id,
        comment=payload.comment,
        ctx=ctx,
    )
    return ApprovalResponse(
        leave_request_id=result["leave_request"].id,
        status=result["status"],
        is_final=result["is_final"],
    )


@router.post("/steps/{step_id}/reject", response_model=ApprovalResponse)
def reject_step(
    step_id: UUID,
    payload: ApprovalAction,
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    """Reject a workflow step.
    
    Only the assigned approver can reject.
    Terminates workflow and rejects the leave request.
    """
    result = engine.reject_step(
        step_id=step_id,
        actor_user_id=payload.actor_user_id,
        comment=payload.comment,
        ctx=ctx,
    )
    return ApprovalResponse(
        leave_request_id=result["leave_request"].id,
        status=result["status"],
        is_final=result["is_final"],
    )


@router.post("/{request_id}/withdraw", response_model=ApprovalResponse)
def withdraw_request(
    request_id: UUID,
    payload: WithdrawalRequest,
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    """Withdraw a leave request.
    
    Only the request owner can withdraw.
    Only allowed while status is PENDING_APPROVAL.
    Terminates workflow.
    """
    result = engine.withdraw_request(
        leave_request_id=request_id,
        actor_user_id=payload.actor_user_id,
        reason=payload.reason,
        ctx=ctx,
    )
    return ApprovalResponse(
        leave_request_id=result["leave_request"].id,
        status=result["status"],
        is_final=result["is_final"],
    )
