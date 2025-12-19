# Phase 17: Authentication and RBAC Implementation

## Overview

Implemented production-grade JWT authentication and role-based access control (RBAC) for the Leave Management System.

**Architecture**: Auth is applied at API layer only. Engines remain RBAC-unaware and trust the caller-provided actor_user_id.

---

## What Was Implemented

### 1. **JWT Authentication** (`app/core/security.py`)

**Key Features:**
- Validates Bearer tokens from `Authorization` header
- Decodes and validates JWT signature using HS256
- Checks token expiration (exp claim)
- Extracts required claims: `sub` (user_id), `roles`, `org_id`
- Maps token subject to User record in database
- Validates user is ACTIVE
- Returns `AuthenticatedUser` context with roles

**Dependencies:**
- `get_authenticated_user()` - FastAPI dependency for token validation
- Returns `AuthenticatedUser` with user_id, email, organization_id, roles, sso_subject_id

**Token Structure (from external IdP):**
```json
{
  "sub": "user-uuid-or-email",
  "roles": ["employee", "manager"],
  "org_id": "org-uuid",
  "oid": "azure-ad-object-id",
  "exp": 1703001600
}
```

**Note**: LMS does NOT issue tokens. Tokens come from external IdP (Azure AD, Okta, etc).

---

### 2. **RBAC Enforcement** (`app/core/rbac.py`)

**Roles Defined:**
- **EMPLOYEE** - Apply/view own leave, basic data access
- **MANAGER** - Approve/reject leave for team, team visibility
- **HR_ADMIN** - Configure policies, org-wide reports, all leave visibility
- **SYSTEM_ADMIN** - Full system access, user/role management
- **AUDITOR** - Read-only audit log access

**Core Classes:**

**`RBACContext`** - Wraps authenticated user for permission checks
```python
class RBACContext:
    def has_role(*roles) -> bool        # Any role
    def has_all_roles(*roles) -> bool   # All roles
    def is_system_admin() -> bool
    def is_hr_admin() -> bool
    def is_manager() -> bool
    def is_employee() -> bool
    def is_auditor() -> bool
```

**`OwnershipCheck`** - Helper for ownership validation
```python
OwnershipCheck.check_user_ownership(rbac, resource_user_id)
OwnershipCheck.check_manager_authority(rbac, target_user_id)
```

**Dependency Functions:**
- `get_rbac_context()` - FastAPI dependency returning RBACContext
- `require_roles(*roles)` - Decorator factory for role-based access
- `require_all_roles(*roles)` - Strict multiple role requirement

**Usage in Endpoints:**
```python
@router.post("/leave-requests")
def create_leave_request(
    rbac: RBACContext = Depends(require_roles(UserRole.EMPLOYEE, UserRole.MANAGER)),
    ...
):
    # Only employees or managers can access
    # Ownership checks happen in endpoint before calling engine
    if rbac.is_employee() and request.user_id != rbac.user_id:
        raise HTTPException(403, "Can only create for yourself")
    ...
```

---

### 3. **API Layer Integration** (`app/api/deps.py`)

**Updated `get_audit_context()`:**
- Now accepts optional `AuthenticatedUser` from JWT
- Automatically enriches audit context with authenticated user if JWT provided
- Falls back to header-based context if JWT not used
- All audit logs now include authenticated actor_user_id

**Benefits:**
- Audit trail automatically tracks who performed each action
- No manual actor_id passing needed
- Backward compatible with header-based auth

---

### 4. **Example Endpoints** (`leave_requests_with_auth_example.py`)

Demonstrates proper integration patterns:

**Pattern 1: Public Endpoint**
```python
@router.get("/health")
def health_check():
    return {"status": "ok"}
```

**Pattern 2: Role-Based Access**
```python
@router.post("/{request_id}/submit")
def submit_leave_request(
    rbac: RBACContext = Depends(require_roles(UserRole.EMPLOYEE)),
    ...
):
    # Only authenticated employees can access
    ...
```

**Pattern 3: Ownership Check**
```python
@router.post("/{request_id}/withdraw")
def withdraw_request(
    rbac: RBACContext = Depends(require_roles(UserRole.EMPLOYEE)),
    ...
):
    request = engine.get_leave_request(request_id)
    
    # Ownership check at API layer
    if request.user_id != rbac.user_id:
        raise HTTPException(403, "Can only withdraw own requests")
    
    # Call engine with authenticated actor
    result = engine.withdraw_request(
        request_id=request_id,
        actor_user_id=rbac.user_id,  # Pass authenticated user
        ctx=ctx,  # Audit context includes actor
    )
```

**Pattern 4: Complex Authority Check**
```python
@router.post("/steps/{step_id}/approve")
def approve_step(
    rbac: RBACContext = Depends(require_roles(UserRole.MANAGER, UserRole.HR_ADMIN)),
    ...
):
    step = engine.get_workflow_step(step_id)
    
    # Check if manager is assigned to this step
    if not rbac.is_hr_admin() and rbac.user_id not in step.assigned_users:
        raise HTTPException(403, "Not assigned to this step")
    
    # Proceed with approval
    ...
```

---

## Files Created/Modified

### Created:
- [lms/app/core/security.py](lms/app/core/security.py) - JWT validation and token handling
- [lms/app/core/rbac.py](lms/app/core/rbac.py) - Role-based access control
- [AUTH_RBAC_IMPLEMENTATION.md](AUTH_RBAC_IMPLEMENTATION.md) - Detailed integration guide
- [lms/app/api/v1/endpoints/leave_requests_with_auth_example.py](lms/app/api/v1/endpoints/leave_requests_with_auth_example.py) - Example endpoint patterns

### Modified:
- [lms/app/api/deps.py](lms/app/api/deps.py) - Integrated auth dependencies

---

## Key Design Decisions

### 1. **Authentication ≠ Authorization**
- Security module handles *authentication* (who are you?)
- RBAC module handles *authorization* (what can you do?)
- Clear separation of concerns

### 2. **Engines Remain RBAC-Unaware**
- Engines trust caller-provided actor_user_id
- Engines enforce workflow invariants, NOT RBAC
- All RBAC checks happen at API layer
- Benefit: Engines stay pure domain logic

### 3. **Ownership Checks at API Layer**
- Before calling engine, endpoints verify user has permission
- Example: Employees can only withdraw own requests
- Example: Managers can only approve assigned steps
- Engines don't implement these checks

### 4. **Audit Context Auto-Enrichment**
- `get_audit_context()` automatically includes authenticated user
- No manual actor_id passing to repositories
- All actions attributed to correct user automatically

### 5. **Minimal Changes to Existing Routes**
- Add single dependency to endpoints that need auth
- No business logic changes needed
- Engine calls remain unchanged
- Backward compatible with header-based auth

### 6. **Fail-Safe RBAC**
- Default: deny all
- Explicit role requirements in decorators
- HTTPException(403) on authorization failure
- No silent permission grants

---

## Security Configuration

**In `app/core/config.py`:**
```python
SECRET_KEY: str = "your-secret-key-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
REFRESH_TOKEN_EXPIRE_DAYS: int = 7
OAUTH2_ENABLED: bool = False
OAUTH2_PROVIDER_URL: Optional[str] = None
OAUTH2_CLIENT_ID: Optional[str] = None
OAUTH2_CLIENT_SECRET: Optional[str] = None
```

**For Production:**
- Change SECRET_KEY to strong random string
- Store in HashiCorp Vault or AWS Secrets Manager
- Set OAUTH2_ENABLED = True
- Configure OAUTH2_PROVIDER_URL (Azure AD, Okta)
- Use RS256 algorithm with IdP public keys (instead of HS256)

---

## Testing

**Create test tokens:**
```python
from app.core.security import create_access_token
from app.core.enums import UserRole
from datetime import timedelta

token = create_access_token(
    user_id=UUID("..."),
    organization_id=UUID("..."),
    roles=[UserRole.EMPLOYEE],
    expires_delta=timedelta(hours=24)
)
```

**Use in tests:**
```python
response = client.get(
    "/leave-requests",
    headers={"Authorization": f"Bearer {token}"}
)
assert response.status_code == 200
```

---

## Integration Roadmap

### Phase 17 (Current): Foundation
✅ JWT validation
✅ RBAC roles and dependencies  
✅ API layer integration patterns
✅ Example endpoints
✅ Documentation

### Phase 18: Apply to Endpoints
- [ ] Update leave request endpoints with auth
- [ ] Update user management endpoints
- [ ] Update policy management endpoints
- [ ] Update audit endpoints

### Phase 19: Advanced RBAC
- [ ] Team/reporting hierarchy checks
- [ ] Dynamic policy-based permissions
- [ ] Delegation and escalation
- [ ] Token refresh flow

### Phase 20: External IdP
- [ ] Azure AD integration
- [ ] Okta integration
- [ ] JWKS endpoint support
- [ ] Automatic key rotation

---

## What's NOT Implemented

❌ Token issuance (by LMS)
❌ User registration flows
❌ SSO UI flows
❌ Token refresh endpoints (for now)
❌ OpenID Connect discovery
❌ Multi-tenant OIDC

*These are handled by external IdP*

---

## Backward Compatibility

The auth implementation is **backward compatible**:
- Endpoints without `require_roles()` dependency can still use header-based auth
- `get_audit_context()` works with both JWT and header-based context
- Existing engine calls unchanged
- Can be rolled out endpoint-by-endpoint

---

## Next Steps

1. **Apply to existing endpoints**: Add `rbac` dependencies to leave_requests, users, audit endpoints
2. **Team hierarchy checks**: Verify managers can only approve their team's requests
3. **Integration tests**: Test role-based access control
4. **External IdP**: Configure with Azure AD or Okta
5. **Token management UI**: Create token management endpoints for admins

---

## Documentation

- [AUTH_RBAC_IMPLEMENTATION.md](AUTH_RBAC_IMPLEMENTATION.md) - Full integration guide with patterns and examples
- [lms/app/core/security.py](lms/app/core/security.py) - Detailed docstrings
- [lms/app/core/rbac.py](lms/app/core/rbac.py) - Permission matrix and usage examples
- [leave_requests_with_auth_example.py](lms/app/api/v1/endpoints/leave_requests_with_auth_example.py) - 10 example patterns

---

## Commit Information

```
feat: JWT authentication and RBAC (Phase 17)

- JWT validation with Bearer token extraction
- Role-based access control at API layer
- RBACContext for permission checking
- Ownership/authority validation helpers
- Auto-enriched audit context with authenticated user
- 10 example endpoint patterns
- Complete integration documentation
```
