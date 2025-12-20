"""
Authentication and JWT token handling.

Provides OAuth2/OpenID Connect compatible authentication for FastAPI.
Assumes tokens are issued by an external IdP (Azure AD, Okta, etc).

Architecture:
- LMS does NOT issue tokens
- Tokens are validated and mapped to User records
- Audit context is enriched with authenticated user info
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, cast
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt  # type: ignore[import-untyped]
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from ..repositories import AuditRepository, UserRepository
from .config import get_settings
from .database import get_db
from .enums import UserRole

# HTTP Bearer scheme for token extraction
security = HTTPBearer()


class TokenPayload(BaseModel):
    """JWT token claims structure.

    Assumes token issued by external IdP and includes:
    - sub: user_id (typically UUID or email)
    - roles: list of role strings
    - org_id: organization_id (UUID)
    - oid: Azure AD object ID (optional)
    - exp: expiration timestamp
    """

    sub: str  # user_id or email
    roles: list[str]
    org_id: str
    oid: Optional[str] = None  # Azure AD object ID
    exp: Optional[int] = None


class AuthenticatedUser(BaseModel):
    """User context after successful authentication."""

    user_id: UUID
    email: Optional[str] = None
    organization_id: UUID
    roles: list[UserRole]
    sso_subject_id: Optional[str] = None  # For token re-mapping


def decode_token(token: str) -> TokenPayload:
    """Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        TokenPayload with validated claims

    Raises:
        HTTPException(401): Invalid, expired, or malformed token
    """
    try:
        # In production: get_jwks_client() to fetch public keys from IdP
        # For now, using HS256 with shared secret from config
        payload = jwt.decode(
            token,
            get_settings().SECRET_KEY or "your-secret-key",
            algorithms=["HS256"],
        )

        # Validate required claims
        token_data = TokenPayload(**payload)

        # Check expiration
        if token_data.exp and datetime.utcfromtimestamp(token_data.exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token_data

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token claims: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    """FastAPI dependency to extract and validate authenticated user from JWT.

    Process:
    1. Extract Bearer token from Authorization header
    2. Decode and validate JWT signature, expiry, claims
    3. Map token sub (user_id or email) to User record
    4. Return authenticated user context with roles

    Args:
        credentials: HTTP Authorization header with Bearer token
        db: Database session

    Returns:
        AuthenticatedUser with user_id, roles, org_id

    Raises:
        HTTPException(401): Invalid/missing token
        HTTPException(403): User not found or inactive
    """
    token = credentials.credentials

    # Decode token
    token_data = decode_token(token)

    # Map token subject to User record
    # Assumes token.sub is either UUID or email
    user_repo = UserRepository(db)
    user = None

    try:
        # Try interpreting sub as UUID first
        user_id = UUID(token_data.sub)
        user = user_repo.get(user_id)
    except ValueError:
        # If not UUID, try email
        user = user_repo.get_by_email(token_data.sub)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found",
        )

    # Validate user is active
    from .enums import UserStatus

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.status.value}",
        )

    # Validate org_id matches
    if str(user.organization_id) != token_data.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token organization does not match user organization",
        )

    # Map string roles from token to UserRole enum
    try:
        user_roles: list[UserRole] = [UserRole(role) for role in token_data.roles]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid role in token: {e}",
        )

    return AuthenticatedUser(
        user_id=cast(UUID, user.id),
        email=cast(str, user.email) if user.email else None,
        organization_id=cast(UUID, user.organization_id),
        roles=user_roles,
        sso_subject_id=token_data.oid,  # Azure AD oid for re-mapping
    )


def create_access_token(
    user_id: UUID,
    organization_id: UUID,
    roles: list[UserRole],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token.

    NOTE: This is for testing/development only. In production,
    tokens are issued by the external IdP (Azure AD, Okta, etc).

    Args:
        user_id: User UUID
        organization_id: Organization UUID
        roles: User roles
        expires_delta: Token expiration time

    Returns:
        JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=24)

    expire = datetime.utcnow() + expires_delta

    to_encode: Dict[str, Any] = {
        "sub": str(user_id),
        "org_id": str(organization_id),
        "roles": [role.value for role in roles],
        "exp": int(expire.timestamp()),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        get_settings().SECRET_KEY or "your-secret-key",
        algorithm="HS256",
    )

    return encoded_jwt
