"""Leave request endpoints.

Controllers contain no business logic; they call engines.

SECURITY NOTE: Actor identity comes from authenticated JWT, never from payload.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ....core.enums import UserRole
from ....core.rbac import RBACContext, require_roles
from ....core.security import AuthenticatedUser, get_authenticated_user
from ....engines import LeaveEngine
from ....repositories import AuditContext
from ....schemas.leave import (
    ApprovalResponse,
    LeaveRequestCommentCreate,
    LeaveRequestCreate,
    LeaveRequestResponse,
    SubmitResponse,
)
from ...deps import get_audit_context, get_leave_engine

router = APIRouter()


class ApprovalActionPayload(BaseModel):
    """Payload for approval/rejection (actor comes from JWT, not payload)."""

    comment: Optional[str] = None


class WithdrawalPayload(BaseModel):
    """Payload for withdrawal (actor comes from JWT, not payload)."""

    reason: Optional[str] = None


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
    payload: ApprovalActionPayload,
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
    auth_user: AuthenticatedUser = Depends(get_authenticated_user),
    rbac: RBACContext = Depends(
        require_roles(UserRole.MANAGER, UserRole.HR_ADMIN, UserRole.SYSTEM_ADMIN)
    ),
):
    """Approve a workflow step.

    Only the assigned approver can approve (enforced by engine).
    Activates next step or finalizes workflow.

    SECURITY: Actor identity comes from authenticated JWT.
    """
    result = engine.approve_step(
        step_id=step_id,
        actor_user_id=auth_user.user_id,  # From JWT, not payload
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
    payload: ApprovalActionPayload,
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
    auth_user: AuthenticatedUser = Depends(get_authenticated_user),
    rbac: RBACContext = Depends(
        require_roles(UserRole.MANAGER, UserRole.HR_ADMIN, UserRole.SYSTEM_ADMIN)
    ),
):
    """Reject a workflow step.

    Only the assigned approver can reject (enforced by engine).
    Terminates workflow and rejects the leave request.

    SECURITY: Actor identity comes from authenticated JWT.
    """
    result = engine.reject_step(
        step_id=step_id,
        actor_user_id=auth_user.user_id,  # From JWT, not payload
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
    payload: WithdrawalPayload,
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
    auth_user: AuthenticatedUser = Depends(get_authenticated_user),
):
    """Withdraw a leave request.

    Only the request owner can withdraw (enforced by engine).
    Only allowed while status is PENDING_APPROVAL.
    Terminates workflow.

    SECURITY: Actor identity comes from authenticated JWT.
    """
    result = engine.withdraw_request(
        leave_request_id=request_id,
        actor_user_id=auth_user.user_id,  # From JWT, not payload
        reason=payload.reason,
        ctx=ctx,
    )
    return ApprovalResponse(
        leave_request_id=result["leave_request"].id,
        status=result["status"],
        is_final=result["is_final"],
    )
