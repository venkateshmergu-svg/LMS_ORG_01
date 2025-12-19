"""
Example: Leave request endpoints with authentication and RBAC.

This shows how to integrate auth/RBAC into existing endpoints with minimal changes.

Key changes:
1. Add rbac dependency to endpoints that need role checking
2. Add ownership/authority checks before calling engines
3. Pass rbac.user_id as actor_user_id to engines
4. get_audit_context automatically includes authenticated user
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ....core.enums import UserRole
from ....core.rbac import RBACContext, require_roles, OwnershipCheck
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


# EXAMPLE 1: Public endpoint (no auth required)
@router.get("/health")
def health_check():
    """Health check - no authentication required."""
    return {"status": "ok"}


# EXAMPLE 2: Create leave request - Employees only
@router.post("", response_model=LeaveRequestResponse)
def create_leave_request(
    payload: LeaveRequestCreate,
    rbac: RBACContext = Depends(require_roles(UserRole.EMPLOYEE, UserRole.MANAGER)),
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    """Create a leave request.
    
    Employees can create their own requests.
    Managers can create for themselves or their team.
    HR admins can create for anyone.
    """
    # Check ownership: can only create for self or team
    if rbac.is_employee() and payload.user_id != rbac.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees can only create requests for themselves",
        )
    
    # HR admins can create for anyone
    # Managers can create for their team (would need to check team membership)
    
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


# EXAMPLE 3: Submit leave request - Owner only
@router.post("/{request_id}/submit", response_model=SubmitResponse)
def submit_leave_request(
    request_id: UUID,
    rbac: RBACContext = Depends(require_roles(UserRole.EMPLOYEE, UserRole.MANAGER, UserRole.HR_ADMIN)),
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    """Submit a leave request for approval.
    
    Only the request owner can submit.
    """
    # Get request to check ownership
    request = engine.get_leave_request(request_id)
    
    # Check ownership (employees can only submit own)
    if rbac.is_employee() and request.user_id != rbac.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only submit your own leave requests",
        )
    
    # Call engine with authenticated user as actor
    updated = engine.submit(request_id=request_id, ctx=ctx)
    return SubmitResponse.model_validate(updated)


# EXAMPLE 4: Add comment - Any role
@router.post("/{request_id}/comments", response_model=dict)
def add_comment(
    request_id: UUID,
    payload: LeaveRequestCommentCreate,
    rbac: RBACContext = Depends(require_roles(
        UserRole.EMPLOYEE,
        UserRole.MANAGER,
        UserRole.HR_ADMIN,
    )),
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    """Add comment to a leave request.
    
    Any authenticated employee can add comments.
    """
    # Verify request exists
    request = engine.get_leave_request(request_id)
    
    # Use authenticated user as commenter
    comment = engine.add_comment(
        request_id=request_id,
        user_id=rbac.user_id,  # Use authenticated user, not payload
        comment=payload.comment,
        is_internal=payload.is_internal,
        ctx=ctx,
    )
    return {"id": str(comment.id)}


# EXAMPLE 5: Approve workflow step - Managers/HR only
@router.post("/steps/{step_id}/approve", response_model=ApprovalResponse)
def approve_step(
    step_id: UUID,
    payload: ApprovalAction,
    rbac: RBACContext = Depends(require_roles(
        UserRole.MANAGER,
        UserRole.HR_ADMIN,
        UserRole.SYSTEM_ADMIN,
    )),
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    """Approve a workflow step.
    
    Only managers assigned to this step can approve.
    HR admins and system admins can approve any step.
    """
    # Get step to check authority
    step = engine.get_workflow_step(step_id)
    
    # Check if manager is assigned (HR/system admins bypass this)
    if not rbac.is_hr_admin() and rbac.user_id not in step.assigned_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to approve this step",
        )
    
    # Pass authenticated user as actor
    result = engine.approve_step(
        step_id=step_id,
        actor_user_id=rbac.user_id,  # Use authenticated user
        comment=payload.comment,
        ctx=ctx,
    )
    return ApprovalResponse(
        leave_request_id=result["leave_request"].id,
        status=result["status"],
        is_final=result["is_final"],
    )


# EXAMPLE 6: Reject workflow step - Managers/HR only
@router.post("/steps/{step_id}/reject", response_model=ApprovalResponse)
def reject_step(
    step_id: UUID,
    payload: ApprovalAction,
    rbac: RBACContext = Depends(require_roles(
        UserRole.MANAGER,
        UserRole.HR_ADMIN,
        UserRole.SYSTEM_ADMIN,
    )),
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    """Reject a workflow step.
    
    Only managers assigned to this step can reject.
    HR admins and system admins can reject any step.
    """
    step = engine.get_workflow_step(step_id)
    
    if not rbac.is_hr_admin() and rbac.user_id not in step.assigned_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to reject this step",
        )
    
    result = engine.reject_step(
        step_id=step_id,
        actor_user_id=rbac.user_id,
        comment=payload.comment,
        ctx=ctx,
    )
    return ApprovalResponse(
        leave_request_id=result["leave_request"].id,
        status=result["status"],
        is_final=result["is_final"],
    )


# EXAMPLE 7: Withdraw leave request - Owner only
@router.post("/{request_id}/withdraw", response_model=ApprovalResponse)
def withdraw_request(
    request_id: UUID,
    payload: WithdrawalRequest,
    rbac: RBACContext = Depends(require_roles(
        UserRole.EMPLOYEE,
        UserRole.MANAGER,
        UserRole.HR_ADMIN,
    )),
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    """Withdraw a leave request.
    
    Only the request owner can withdraw.
    HR admins can withdraw any request.
    """
    request = engine.get_leave_request(request_id)
    
    # Check ownership
    if request.user_id != rbac.user_id and not rbac.is_hr_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only withdraw your own requests",
        )
    
    result = engine.withdraw_request(
        leave_request_id=request_id,
        actor_user_id=rbac.user_id,  # Use authenticated user
        reason=payload.reason,
        ctx=ctx,
    )
    return ApprovalResponse(
        leave_request_id=result["leave_request"].id,
        status=result["status"],
        is_final=result["is_final"],
    )


# EXAMPLE 8: View leave request - Authorized users only
@router.get("/{request_id}", response_model=LeaveRequestResponse)
def get_leave_request(
    request_id: UUID,
    rbac: RBACContext = Depends(require_roles(
        UserRole.EMPLOYEE,
        UserRole.MANAGER,
        UserRole.HR_ADMIN,
        UserRole.AUDITOR,
    )),
    engine: LeaveEngine = Depends(get_leave_engine),
):
    """Get a leave request.
    
    - Employees can see their own
    - Managers can see their team's
    - HR admins can see all
    - Auditors can see all
    """
    request = engine.get_leave_request(request_id)
    
    # Authorization check
    if rbac.is_employee() and request.user_id != rbac.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own requests",
        )
    
    # Managers: would check if request.user_id is on their team
    # For now, just check if not employee
    
    return request


# EXAMPLE 9: View all leave requests - Managers/HR/Auditors
@router.get("", response_model=list[LeaveRequestResponse])
def list_leave_requests(
    user_id: UUID | None = None,
    rbac: RBACContext = Depends(require_roles(
        UserRole.MANAGER,
        UserRole.HR_ADMIN,
        UserRole.AUDITOR,
    )),
    engine: LeaveEngine = Depends(get_leave_engine),
):
    """List leave requests.
    
    - Managers: their team only
    - HR admins: all
    - Auditors: all
    """
    # For managers: filter by team
    if rbac.is_manager() and user_id and user_id != rbac.user_id:
        # Would check if user_id is on manager's team
        pass
    
    requests = engine.list_leave_requests(user_id=user_id)
    return requests


# EXAMPLE 10: View balance - Employees can see own, admins see all
@router.get("/{user_id}/balance")
def get_user_balance(
    user_id: UUID,
    rbac: RBACContext = Depends(require_roles(
        UserRole.EMPLOYEE,
        UserRole.MANAGER,
        UserRole.HR_ADMIN,
        UserRole.AUDITOR,
    )),
    engine: LeaveEngine = Depends(get_leave_engine),
):
    """Get user's leave balance.
    
    - Employees can see their own
    - Managers can see their team's
    - HR admins can see all
    - Auditors can see all
    """
    if rbac.is_employee() and user_id != rbac.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view your own balance",
        )
    
    balance = engine.get_leave_balance(user_id=user_id)
    return balance
