"""FastAPI dependencies.

Controllers should depend on engines, not repositories directly.

All dependencies are injected with a UnitOfWork instance that manages
transaction lifecycle. All repositories in a single request share the same
database session and participate in a single transaction.

Authentication:
- get_authenticated_user: Validates JWT and returns user context
- get_rbac_context: Provides role-based access control
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from ..core.database import get_uow
from ..core.security import AuthenticatedUser, get_authenticated_user
from ..core.rbac import RBACContext, get_rbac_context
from ..core.unit_of_work import UnitOfWork
from ..engines import AuditEngine, LeaveEngine, PolicyEngine, UserEngine, WorkflowEngine
from ..repositories import (
    AccrualScheduleRepository,
    AuditContext,
    AuditRepository,
    BalanceTransactionRepository,
    DelegationRepository,
    LeaveBalanceRepository,
    LeavePolicyRepository,
    LeaveRequestCommentRepository,
    LeaveRequestDateRepository,
    LeaveRequestRepository,
    LeaveTypeRepository,
    PolicyAssignmentRepository,
    UserRepository,
    WorkflowConfigurationRepository,
    WorkflowStepRepository,
)


def get_audit_context(
    x_actor_id: Optional[str] = Header(default=None),
    x_organization_id: Optional[str] = Header(default=None),
    x_request_id: Optional[str] = Header(default=None),
    x_session_id: Optional[str] = Header(default=None),
    auth_user: Optional[AuthenticatedUser] = Depends(get_authenticated_user),
) -> AuditContext:
    """Build audit context from headers and authenticated user.
    
    If JWT authentication is enabled, auth_user will be populated.
    Falls back to header-based context if JWT is not used.
    
    Args:
        x_actor_id: Header override for actor_id
        x_organization_id: Header override for organization_id
        x_request_id: Request tracking ID
        x_session_id: Session tracking ID
        auth_user: Authenticated user from JWT (optional)
        
    Returns:
        AuditContext with actor and organization info
    """
    # Use authenticated user if available, fall back to headers
    if auth_user:
        actor_id = auth_user.user_id
        org_id = auth_user.organization_id
        actor_type = "user"
    else:
        actor_id = UUID(x_actor_id) if x_actor_id else None
        org_id = UUID(x_organization_id) if x_organization_id else None
        actor_type = "system" if actor_id is None else "user"
    
    return AuditContext(
        actor_id=actor_id,
        actor_type=actor_type,
        organization_id=org_id,
        request_id=x_request_id,
        session_id=x_session_id,
    )


def get_audit_engine(uow: UnitOfWork = Depends(get_uow)) -> AuditEngine:
    """Inject AuditEngine with transactional session from UnitOfWork."""
    return AuditEngine(uow.session)


def get_user_engine(uow: UnitOfWork = Depends(get_uow)) -> UserEngine:
    """Inject UserEngine with transactional session and repositories from UnitOfWork."""
    audit_repo = AuditRepository(uow.session)
    user_repo = UserRepository(uow.session, audit_repo=audit_repo)
    return UserEngine(uow.session, user_repo=user_repo)


def get_leave_engine(
    uow: UnitOfWork = Depends(get_uow),
    ctx: AuditContext = Depends(get_audit_context),
) -> LeaveEngine:
    """Inject LeaveEngine with transactional session and all repositories from UnitOfWork.
    
    All repositories in this request share the same session and transaction,
    ensuring atomicity of leave request operations.
    """
    # Repositories - all use the same transactional session from the UnitOfWork
    audit_repo = AuditRepository(uow.session)

    user_repo = UserRepository(uow.session, audit_repo=audit_repo)
    leave_type_repo = LeaveTypeRepository(uow.session, audit_repo=audit_repo)
    leave_policy_repo = LeavePolicyRepository(uow.session, audit_repo=audit_repo)
    assignment_repo = PolicyAssignmentRepository(uow.session, audit_repo=audit_repo)
    balance_repo = LeaveBalanceRepository(uow.session, audit_repo=audit_repo)

    request_repo = LeaveRequestRepository(uow.session, audit_repo=audit_repo)
    request_date_repo = LeaveRequestDateRepository(uow.session, audit_repo=audit_repo)
    request_comment_repo = LeaveRequestCommentRepository(uow.session, audit_repo=audit_repo)

    # Other repos (not yet used by skeleton but wired for future engines)
    BalanceTransactionRepository(uow.session, audit_repo=audit_repo)
    AccrualScheduleRepository(uow.session, audit_repo=audit_repo)

    workflow_repo = WorkflowConfigurationRepository(uow.session, audit_repo=audit_repo)
    step_repo = WorkflowStepRepository(uow.session, audit_repo=audit_repo)
    delegation_repo = DelegationRepository(uow.session, audit_repo=audit_repo)

    # Engines - orchestrate domain logic, unaware of transaction boundaries
    policy_engine = PolicyEngine(
        uow.session,
        policy_repo=leave_policy_repo,
        assignment_repo=assignment_repo,
        balance_repo=balance_repo,
    )
    workflow_engine = WorkflowEngine(
        uow.session,
        workflow_repo=workflow_repo,
        step_repo=step_repo,
        delegation_repo=delegation_repo,
        user_repo=user_repo,
        leave_request_repo=request_repo,
        audit_repo=audit_repo,
    )

    # Note: ctx is passed separately; controller passes it to engine calls.
    return LeaveEngine(
        uow.session,
        user_repo=user_repo,
        leave_type_repo=leave_type_repo,
        request_repo=request_repo,
        request_date_repo=request_date_repo,
        request_comment_repo=request_comment_repo,
        policy_engine=policy_engine,
        workflow_engine=workflow_engine,
    )
