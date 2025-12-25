"""
Dev-only authentication stub.

This module provides a stub implementation of get_authenticated_user that:
- Accepts ANY Bearer token value (no validation)
- Returns a fixed user principal for local development

Usage:
    In DEBUG mode, main.py applies dependency_overrides to swap
    the real auth dependency with this stub.

SECURITY WARNING:
    This stub should NEVER be used in production. It completely
    bypasses authentication and returns a hardcoded user.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .enums import UserRole
from .security import AuthenticatedUser

# HTTP Bearer scheme - accepts any token
_dev_security = HTTPBearer(auto_error=False)

# Fixed dev user principal
# These UUIDs are deterministic for local dev consistency
DEV_USER_ID = UUID("8526a36a-ae2c-4e58-938a-7047a5eb8873")
DEV_ORG_ID = UUID("329701ad-cf39-4e64-8968-1f0593ff2b0a")
DEV_EMAIL = "dev@example.com"
DEV_ROLES = [UserRole.SYSTEM_ADMIN, UserRole.MANAGER, UserRole.EMPLOYEE]


async def get_authenticated_user_stub(
    credentials: HTTPAuthorizationCredentials | None = Depends(_dev_security),
) -> AuthenticatedUser:
    """Dev-only stub that accepts any Bearer token.

    Returns a fixed user principal regardless of token content.
    If no token is provided, still returns the dev user (fully open).

    Args:
        credentials: Optional HTTP Authorization header

    Returns:
        Fixed AuthenticatedUser for dev/testing
    """
    # Always return the fixed dev user
    return AuthenticatedUser(
        user_id=DEV_USER_ID,
        email=DEV_EMAIL,
        organization_id=DEV_ORG_ID,
        roles=DEV_ROLES,
        sso_subject_id=None,
    )


def get_dev_user_principal() -> AuthenticatedUser:
    """Get the fixed dev user principal (non-async version for tests)."""
    return AuthenticatedUser(
        user_id=DEV_USER_ID,
        email=DEV_EMAIL,
        organization_id=DEV_ORG_ID,
        roles=DEV_ROLES,
        sso_subject_id=None,
    )
