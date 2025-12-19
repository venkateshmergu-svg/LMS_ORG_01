"""
Authentication and RBAC Integration Guide

Architecture Overview
====================

The LMS uses JWT-based authentication with role-based access control (RBAC).

Flow:
1. Client sends request with Authorization: Bearer <JWT>
2. get_authenticated_user() validates JWT and maps to User record
3. get_rbac_context() enriches context with user roles
4. API endpoints use role dependencies to enforce RBAC
5. Audit context automatically includes authenticated user
6. Engines receive actor_user_id and trust caller-provided context


Authentication Flow
===================

REQUEST:
  GET /leave-requests
  Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

VALIDATION (app/core/security.py):
  1. Extract token from Authorization header
  2. Decode JWT signature (validate with IdP public key)
  3. Check expiration (exp claim)
  4. Validate required claims: sub, roles, org_id
  5. Map token.sub to User record in database
  6. Verify user.status == ACTIVE
  7. Verify user.org_id == token.org_id
  8. Return AuthenticatedUser with roles

RESULT:
  AuthenticatedUser(
    user_id=UUID(...),
    email="user@org.com",
    organization_id=UUID(...),
    roles=[UserRole.EMPLOYEE, UserRole.MANAGER],
    sso_subject_id="abc123"  # For re-mapping
  )


RBAC Enforcement
================

Requirements by Role:

EMPLOYEE:
  - create_leave_request: Own request only
  - view_leave_request: Own request only
  - withdraw_request: Own request only
  - view_balance: Own balance only

MANAGER:
  - All EMPLOYEE permissions
  - approve_leave: Assigned workflow steps only
  - reject_leave: Assigned workflow steps only
  - view_team_leaves: Reporting employees only

HR_ADMIN:
  - View/manage all leave requests
  - Configure leave policies
  - View org-wide reports
  - Does NOT include user management

SYSTEM_ADMIN:
  - All RBAC permissions
  - User and role management

AUDITOR:
  - Read-only audit log access
  - Read-only leave request/balance access


Integration in Endpoints
=======================

OPTION 1: Optional Authentication (Public API)
----------------------------------------------
@router.get("/health")
def health_check():
    # No authentication required
    return {"status": "ok"}


OPTION 2: Require Any Role
---------------------------
@router.get("/leave-requests/{request_id}")
def get_leave_request(
    request_id: UUID,
    rbac: RBACContext = Depends(require_roles(UserRole.EMPLOYEE, UserRole.AUDITOR)),
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    # User must have EMPLOYEE or AUDITOR role
    # Check ownership/authority before querying
    
    request = engine.get_leave_request(request_id)
    
    # Employee can see only their own
    if rbac.is_employee() and request.user_id != rbac.user_id:
        raise HTTPException(status_code=403)
    
    return request


OPTION 3: Require Specific Role
--------------------------------
@router.post("/leave-policies")
def create_policy(
    payload: LeavePolicyCreate,
    rbac: RBACContext = Depends(require_roles(UserRole.HR_ADMIN, UserRole.SYSTEM_ADMIN)),
    engine: PolicyEngine = Depends(get_policy_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    # Only HR admins and system admins can create policies
    # audit context automatically includes authenticated user
    
    policy = engine.create_policy(
        name=payload.name,
        leave_type_id=payload.leave_type_id,
        accrual_rule=payload.accrual_rule,
        ctx=ctx,
    )
    return policy


OPTION 4: Complex Ownership Check
----------------------------------
@router.post("/leave-requests/{request_id}/withdraw")
def withdraw_leave_request(
    request_id: UUID,
    rbac: RBACContext = Depends(require_roles(UserRole.EMPLOYEE)),
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    # Employee role required
    
    request = engine.get_leave_request(request_id)
    
    # Check ownership
    if request.user_id != rbac.user_id:
        raise HTTPException(
            status_code=403,
            detail="Can only withdraw own leave requests"
        )
    
    # Call engine with authenticated actor_id
    # Engine is unaware of RBAC, only enforces workflow invariants
    result = engine.withdraw_request(
        request_id=request_id,
        actor_id=rbac.user_id,  # Explicitly pass authenticated user
        ctx=ctx,
    )
    
    return result


OPTION 5: Manager Approval (Workflow Authority)
------------------------------------------------
@router.post("/steps/{step_id}/approve")
def approve_step(
    step_id: UUID,
    payload: ApprovalAction,
    rbac: RBACContext = Depends(require_roles(UserRole.MANAGER, UserRole.HR_ADMIN)),
    engine: LeaveEngine = Depends(get_leave_engine),
    ctx: AuditContext = Depends(get_audit_context),
):
    # Manager or HR admin role required
    
    step = engine.get_workflow_step(step_id)
    
    # Check if manager is assigned this step
    # In production: verify rbac.user_id in step.assigned_users
    if not rbac.is_hr_admin() and rbac.user_id not in step.assigned_users:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned this workflow step"
        )
    
    # Call engine
    result = engine.approve_step(
        step_id=step_id,
        actor_id=rbac.user_id,
        comments=payload.comments,
        ctx=ctx,
    )
    
    return result


Testing and Development
=======================

Create test tokens:
    from app.core.security import create_access_token
    
    token = create_access_token(
        user_id=UUID("..."),
        organization_id=UUID("..."),
        roles=[UserRole.EMPLOYEE],
        expires_delta=timedelta(hours=24)
    )

Use in tests:
    response = client.get(
        "/leave-requests",
        headers={"Authorization": f"Bearer {token}"}
    )


Configuration
=============

In app/core/config.py:

SECRET_KEY: str
  - JWT signing key
  - In production: fetch from HashiCorp Vault or AWS Secrets Manager
  - Used for HS256 signing (for local testing)

JWT_ALGORITHM: str = "HS256"
  - Default: HS256 (shared secret)
  - Production: RS256 (public/private keys from IdP)

JWT_EXPIRATION_HOURS: int = 24
  - Default token lifetime

EXTERNAL_JWT_PROVIDER: Optional[str] = None
  - Optional JWKS endpoint for token validation
  - Example: "https://login.microsoftonline.com/{tenant}/.well-known/openid-configuration"


Migration Path
==============

Phase 1 (Current):
  - JWT validation with shared secret (HS256)
  - Token mapping to User records
  - Basic RBAC at API layer

Phase 2:
  - Integrate with Azure AD / Okta JWKS endpoint
  - Automatic key rotation
  - Token refresh flow

Phase 3:
  - SSO UI integration (if needed)
  - Delegated token validation
  - Advanced scoping and consent


Key Design Principles
=====================

1. Authentication ≠ Authorization
   - Security module handles authentication (who are you?)
   - RBAC module handles authorization (what can you do?)

2. Engines are RBAC-unaware
   - Engines receive actor_user_id and trust it
   - Engines enforce workflow invariants, not RBAC
   - All RBAC checks happen at API layer

3. Audit context includes actor
   - AuthenticatedUser automatically injected into AuditContext
   - All domain changes attributed to authenticated user
   - No need to manually pass actor_id to audit_repo

4. Minimal changes to existing code
   - Existing endpoints only need role dependency added
   - Existing engine calls remain unchanged
   - Ownership checks isolated to endpoint layer

5. Fail-safe RBAC
   - Default: deny all
   - Explicit role requirements in endpoint decorators
   - Ownership checks required for resource access
   - HTTPException(403) on authorization failure
"""
