"""
Role-Based Access Control (RBAC).

RBAC enforcement happens at the API layer only.
- Engines trust the caller-provided actor_user_id
- Engines enforce workflow invariants, not RBAC
- Ownership checks happen in endpoints before calling engines

Role hierarchy:
- EMPLOYEE: Apply leave, view own data
- MANAGER: Approve/reject leave for reporting employees
- HR_ADMIN: Configure policies, view org reports
- SYSTEM_ADMIN: User/role management
- AUDITOR: Read-only audit log access
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status

from .enums import UserRole
from .security import AuthenticatedUser, get_authenticated_user


class RBACContext:
    """Wraps authenticated user for RBAC checks."""

    def __init__(self, user: AuthenticatedUser):
        self.user = user
        self.user_id = user.user_id
        self.roles = user.roles
        self.organization_id = user.organization_id

    def has_role(self, *required_roles: UserRole) -> bool:
        """Check if user has any of the required roles."""
        return any(role in self.roles for role in required_roles)

    def has_all_roles(self, *required_roles: UserRole) -> bool:
        """Check if user has all of the required roles."""
        return all(role in self.roles for role in required_roles)

    def is_system_admin(self) -> bool:
        """Convenience check for system admin."""
        return self.has_role(UserRole.SYSTEM_ADMIN)

    def is_hr_admin(self) -> bool:
        """Convenience check for HR admin."""
        return self.has_role(UserRole.HR_ADMIN)

    def is_manager(self) -> bool:
        """Convenience check for manager."""
        return self.has_role(UserRole.MANAGER)

    def is_employee(self) -> bool:
        """Convenience check for employee."""
        return self.has_role(UserRole.EMPLOYEE)

    def is_auditor(self) -> bool:
        """Convenience check for auditor."""
        return self.has_role(UserRole.AUDITOR)


async def get_rbac_context(
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> RBACContext:
    """FastAPI dependency to get RBAC context from authenticated user."""
    return RBACContext(user)


def require_roles(*required_roles: UserRole):
    """Dependency factory for role-based access control.
    
    Usage in endpoints:
        @router.get("/admin-only")
        def admin_endpoint(rbac: RBACContext = Depends(require_roles(UserRole.SYSTEM_ADMIN))):
            ...
    
    Args:
        *required_roles: Roles required to access the endpoint
        
    Returns:
        Dependency function that checks roles
        
    Raises:
        HTTPException(403): User does not have required role
    """

    async def check_roles(rbac: RBACContext = Depends(get_rbac_context)) -> RBACContext:
        if not rbac.has_role(*required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This operation requires one of: {', '.join(r.value for r in required_roles)}",
            )
        return rbac

    return check_roles


def require_all_roles(*required_roles: UserRole):
    """Dependency factory for multiple required roles.
    
    Usage in endpoints:
        @router.post("/sensitive")
        def sensitive_endpoint(
            rbac: RBACContext = Depends(require_all_roles(UserRole.SYSTEM_ADMIN, UserRole.AUDITOR))
        ):
            ...
    
    Args:
        *required_roles: All roles required to access the endpoint
        
    Returns:
        Dependency function that checks all roles
        
    Raises:
        HTTPException(403): User does not have all required roles
    """

    async def check_all_roles(rbac: RBACContext = Depends(get_rbac_context)) -> RBACContext:
        if not rbac.has_all_roles(*required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This operation requires all of: {', '.join(r.value for r in required_roles)}",
            )
        return rbac

    return check_all_roles


class OwnershipCheck:
    """Helper for ownership validation in endpoints.
    
    Ownership checks happen at API layer before calling engines.
    Examples:
    - Employee can withdraw only their own leave request
    - Manager can approve only assigned workflow steps
    """

    @staticmethod
    def check_user_ownership(rbac: RBACContext, resource_user_id: UUID) -> None:
        """Verify user owns the resource or is admin.
        
        Args:
            rbac: RBAC context
            resource_user_id: User ID of resource owner
            
        Raises:
            HTTPException(403): User does not own resource
        """
        if rbac.user_id != resource_user_id and not rbac.is_system_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

    @staticmethod
    def check_manager_authority(
        rbac: RBACContext,
        target_user_id: UUID,
        user_repo: Optional[object] = None,
    ) -> None:
        """Verify user is manager of target employee.
        
        Args:
            rbac: RBAC context
            target_user_id: Employee being managed
            user_repo: UserRepository for manager lookup (optional)
            
        Raises:
            HTTPException(403): User is not manager
        """
        if not rbac.has_role(UserRole.MANAGER, UserRole.HR_ADMIN, UserRole.SYSTEM_ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only managers can approve leave",
            )
        
        # In production, verify user is actual manager of target_user
        # using user_repo if provided
        # For now, just check role


# Role permission matrices (reference for implementation)
ROLE_PERMISSIONS = {
    UserRole.EMPLOYEE: {
        "create_leave_request": True,
        "view_own_leave_requests": True,
        "view_own_balance": True,
        "withdraw_own_request": True,
        "view_org_reports": False,
        "approve_leave": False,
        "configure_policies": False,
        "manage_users": False,
        "view_audit_logs": False,
    },
    UserRole.MANAGER: {
        "create_leave_request": True,
        "view_own_leave_requests": True,
        "view_own_balance": True,
        "withdraw_own_request": True,
        "view_team_leave_requests": True,
        "view_team_balance": True,
        "approve_leave": True,
        "view_org_reports": False,
        "configure_policies": False,
        "manage_users": False,
        "view_audit_logs": False,
    },
    UserRole.HR_ADMIN: {
        "create_leave_request": True,
        "view_all_leave_requests": True,
        "view_all_balances": True,
        "approve_leave": True,
        "configure_policies": True,
        "manage_users": False,
        "view_org_reports": True,
        "view_audit_logs": True,
    },
    UserRole.SYSTEM_ADMIN: {
        "create_leave_request": True,
        "view_all_leave_requests": True,
        "view_all_balances": True,
        "approve_leave": True,
        "configure_policies": True,
        "manage_users": True,
        "manage_roles": True,
        "view_org_reports": True,
        "view_audit_logs": True,
    },
    UserRole.AUDITOR: {
        "view_all_leave_requests": True,
        "view_all_balances": True,
        "view_org_reports": True,
        "view_audit_logs": True,
    },
}
