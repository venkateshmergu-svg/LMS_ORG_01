"""Authentication endpoints.

NOTE: The core architecture assumes tokens are issued by an external IdP.
These endpoints provide a minimal local-dev compatible surface so the
frontend can run end-to-end without an external OAuth provider.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ....core.config import get_settings
from ....core.database import get_db
from ....core.enums import AccrualFrequency, UserRole, UserStatus
from ....core.security import (
    AuthenticatedUser,
    create_access_token,
    decode_token,
    get_authenticated_user,
)
from ....models.leave import LeaveBalance, LeavePolicy, LeaveType
from ....models.user import Organization, User

router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class MeResponse(BaseModel):
    id: str
    email: str
    full_name: str
    roles: list[str]


def _ensure_dev_user(db: Session) -> User:
    """Backward-compatible helper for local dev.

    Kept for compatibility; prefer `_ensure_dev_user_by_email`.
    """

    return _ensure_dev_user_by_email(
        db,
        email="alice@example.com",
        first_name="Alice",
        last_name="Doe",
    )


def _generate_employee_id(db: Session, email: str) -> str:
    base = "DEV_" + email.split("@", 1)[0].upper().replace(".", "_")
    base = base[:45]  # leave room for suffix
    candidate = base
    suffix = 1
    while (
        db.execute(select(User).where(User.employee_id == candidate)).scalars().first()
        is not None
    ):
        suffix += 1
        candidate = f"{base}_{suffix}"[:50]
    return candidate


def _ensure_dev_user_by_email(
    db: Session, *, email: str, first_name: str, last_name: str
) -> User:
    """Ensure a deterministic dev org+user exist.

    Keeps local dev friction low by creating the minimum required rows.
    """

    org = (
        db.execute(select(Organization).where(Organization.code == "ORG1"))
        .scalars()
        .first()
    )
    if org is None:
        org = Organization(code="ORG1", name="Org 1")
        db.add(org)
        db.flush()  # populate org.id

    user = db.execute(select(User).where(User.email == email)).scalars().first()
    if user is None:
        user = User(
            employee_id=_generate_employee_id(db, email),
            email=email,
            first_name=first_name,
            last_name=last_name,
            organization_id=org.id,
            status=UserStatus.ACTIVE,
        )
        db.add(user)
        db.flush()  # populate user.id

    # Seed minimal leave setup for local dev so UI + APIs work end-to-end.
    _ensure_dev_leave_setup(db, org_id=cast(UUID, org.id), user_id=cast(UUID, user.id))

    db.commit()
    db.refresh(user)
    return user


def _ensure_dev_leave_setup(db: Session, *, org_id: UUID, user_id: UUID) -> None:
    leave_type = (
        db.execute(
            select(LeaveType).where(
                LeaveType.organization_id == org_id,
                LeaveType.code == "ANNUAL",
            )
        )
        .scalars()
        .first()
    )
    if leave_type is None:
        leave_type = LeaveType(
            organization_id=org_id,
            code="ANNUAL",
            name="Annual Leave",
            is_active=True,
            is_paid=True,
            requires_reason=False,
            display_order=0,
        )
        db.add(leave_type)
        db.flush()

    policy = (
        db.execute(
            select(LeavePolicy).where(
                LeavePolicy.organization_id == org_id,
                LeavePolicy.leave_type_id == cast(UUID, leave_type.id),
                LeavePolicy.is_active.is_(True),
            )
        )
        .scalars()
        .first()
    )
    if policy is None:
        policy = LeavePolicy(
            organization_id=org_id,
            leave_type_id=cast(UUID, leave_type.id),
            code="ANNUAL_DEFAULT",
            name="Annual Leave Policy",
            effective_from=datetime.now(timezone.utc),
            effective_to=None,
            accrual_frequency=AccrualFrequency.MONTHLY,
            accrual_amount=1.67,
            is_active=True,
        )
        db.add(policy)
        db.flush()

    year = datetime.now(timezone.utc).year
    period_start = datetime(year, 1, 1, tzinfo=timezone.utc)
    period_end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    balance = (
        db.execute(
            select(LeaveBalance).where(
                LeaveBalance.user_id == user_id,
                LeaveBalance.leave_type_id == cast(UUID, leave_type.id),
                LeaveBalance.period_start == period_start,
            )
        )
        .scalars()
        .first()
    )
    if balance is None:
        balance = LeaveBalance(
            user_id=user_id,
            leave_type_id=cast(UUID, leave_type.id),
            policy_id=cast(UUID, policy.id),
            period_start=period_start,
            period_end=period_end,
            opening_balance=20.0,
            accrued=0.0,
            used=0.0,
            pending=0.0,
            adjusted=0.0,
            carried_forward=0.0,
        )
        db.add(balance)


def _dev_user_from_code(code: str) -> tuple[str, str, str, list[UserRole]]:
    """Map a dev auth code to a test user.

    Supported values:
    - dev (system admin)
    - dev:employee
    - dev:manager
    - dev:hr
    - dev:auditor
    - dev:<email> (defaults to employee)
    """

    if code == "dev":
        return ("alice@example.com", "Alice", "Doe", [UserRole.SYSTEM_ADMIN])

    if not code.startswith("dev:"):
        return ("alice@example.com", "Alice", "Doe", [UserRole.SYSTEM_ADMIN])

    selector = code.split(":", 1)[1].strip()

    presets: dict[str, tuple[str, str, str, list[UserRole]]] = {
        "alice": ("alice@example.com", "Alice", "Doe", [UserRole.SYSTEM_ADMIN]),
        "employee": (
            "eve.employee@example.com",
            "Eve",
            "Employee",
            [UserRole.EMPLOYEE],
        ),
        "manager": ("mike.manager@example.com", "Mike", "Manager", [UserRole.MANAGER]),
        "hr": ("helen.hr@example.com", "Helen", "HR", [UserRole.HR_ADMIN]),
        "auditor": ("andy.auditor@example.com", "Andy", "Auditor", [UserRole.AUDITOR]),
        "sysadmin": ("admin@example.com", "System", "Admin", [UserRole.SYSTEM_ADMIN]),
    }

    preset = presets.get(selector.lower())
    if preset is not None:
        return preset

    # If selector looks like an email, create a generic employee user.
    if "@" in selector and "." in selector:
        local = selector.split("@", 1)[0]
        first = (local.split(".", 1)[0] or "Dev").capitalize()
        last = (local.split(".", 1)[1] if "." in local else "User").capitalize()
        return (selector, first, last, [UserRole.EMPLOYEE])

    return ("alice@example.com", "Alice", "Doe", [UserRole.SYSTEM_ADMIN])


@router.post("/token", response_model=TokenResponse)
async def token_exchange(
    request: Request, db: Session = Depends(get_db)
) -> TokenResponse:
    settings = get_settings()

    # If external OAuth is configured, we intentionally don't implement it here.
    if settings.OAUTH2_ENABLED and not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="External OAuth token exchange is not implemented in this service.",
        )

    content_type = (request.headers.get("content-type") or "").lower()
    if "application/json" in content_type:
        try:
            data = await request.json()
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=400, detail="Invalid JSON body") from exc
    else:
        form = await request.form()
        data = dict(form)

    grant_type = str(data.get("grant_type") or "authorization_code")
    code = str(data.get("code") or "")

    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="Unsupported grant_type")

    # Local-dev convention: frontend uses /auth/callback?code=dev to avoid leaving the SPA.
    if not code.startswith("dev"):
        raise HTTPException(status_code=400, detail="Invalid authorization code")

    email, first_name, last_name, roles = _dev_user_from_code(code)
    user = _ensure_dev_user_by_email(
        db,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )

    access = create_access_token(
        cast(UUID, user.id),
        cast(UUID, user.organization_id),
        roles=roles,
    )

    # For local dev we treat refresh token as a long-lived JWT with same claims.
    refresh = create_access_token(
        cast(UUID, user.id),
        cast(UUID, user.organization_id),
        roles=roles,
    )

    return TokenResponse(access_token=access, refresh_token=refresh)


@router.get("/me", response_model=MeResponse)
def me(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> MeResponse:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    token_data = decode_token(token)

    # Map token subject to DB user
    try:
        user_id = UUID(token_data.sub)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token subject") from exc

    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return MeResponse(
        id=str(user.id),
        email=cast(str, user.email),
        full_name=user.full_name,
        roles=list(token_data.roles),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest) -> TokenResponse:
    token_data = decode_token(payload.refresh_token)

    # Re-issue a fresh token with same claims.
    roles = [UserRole(role) for role in token_data.roles]

    try:
        user_id = UUID(token_data.sub)
        organization_id = UUID(token_data.org_id)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token claims") from exc

    access = create_access_token(
        user_id=user_id,
        organization_id=organization_id,
        roles=roles,
    )

    return TokenResponse(access_token=access, refresh_token=payload.refresh_token)


class DebugMeResponse(BaseModel):
    """Debug endpoint response showing current user principal."""

    sub: str
    email: Optional[str]
    organization_id: str
    roles: list[str]
    debug_mode: bool


@router.get("/debug-me", response_model=DebugMeResponse)
def debug_me(
    auth_user: "AuthenticatedUser" = Depends(get_authenticated_user),
) -> DebugMeResponse:
    """Debug endpoint to inspect the current user principal.

    This endpoint returns the authenticated user context as seen by the
    application. In DEBUG mode, this will show the stub user; in production,
    it shows the real JWT-validated user.

    Useful for:
    - Verifying auth dependency override is working
    - Debugging token claims
    - Testing authentication flow
    """
    from ....core.config import get_settings

    return DebugMeResponse(
        sub=str(auth_user.user_id),
        email=auth_user.email,
        organization_id=str(auth_user.organization_id),
        roles=[role.value for role in auth_user.roles],
        debug_mode=get_settings().DEBUG,
    )
