"""Unit tests for security module - advanced tests.

Tests create_access_token and get_authenticated_user.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from lms.app.core.enums import UserRole, UserStatus
from lms.app.core.security import (
    AuthenticatedUser,
    TokenPayload,
    create_access_token,
    decode_token,
    get_authenticated_user,
)


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_create_token_basic(self):
        """Test basic token creation."""
        user_id = uuid4()
        org_id = uuid4()
        roles = [UserRole.EMPLOYEE]

        with patch("lms.app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test-secret-key"
            token = create_access_token(
                user_id=user_id,
                organization_id=org_id,
                roles=roles,
            )

        assert isinstance(token, str)
        assert len(token) > 0
        # Token should be a valid JWT (3 parts)
        parts = token.split(".")
        assert len(parts) == 3

    def test_create_token_with_expiry(self):
        """Test token creation with custom expiry."""
        user_id = uuid4()
        org_id = uuid4()
        roles = [UserRole.MANAGER]

        with patch("lms.app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test-secret-key"
            token = create_access_token(
                user_id=user_id,
                organization_id=org_id,
                roles=roles,
                expires_delta=timedelta(hours=1),
            )

        assert isinstance(token, str)

    def test_create_token_multiple_roles(self):
        """Test token creation with multiple roles."""
        user_id = uuid4()
        org_id = uuid4()
        roles = [UserRole.EMPLOYEE, UserRole.MANAGER, UserRole.HR_ADMIN]

        with patch("lms.app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test-secret-key"
            token = create_access_token(
                user_id=user_id,
                organization_id=org_id,
                roles=roles,
            )

            # Decode to verify roles - must be within same context
            payload = decode_token(token)
            assert len(payload.roles) == 3

    def test_create_token_fallback_secret(self):
        """Test token creation with fallback secret key."""
        user_id = uuid4()
        org_id = uuid4()
        roles = [UserRole.EMPLOYEE]

        with patch("lms.app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = None
            token = create_access_token(
                user_id=user_id,
                organization_id=org_id,
                roles=roles,
            )

        assert isinstance(token, str)


class TestDecodeTokenAdvanced:
    """Additional tests for decode_token."""

    def test_decode_expired_token(self):
        """Test decoding an expired token."""
        user_id = uuid4()
        org_id = uuid4()

        with patch("lms.app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test-secret-key"
            # Create an expired token
            token = create_access_token(
                user_id=user_id,
                organization_id=org_id,
                roles=[UserRole.EMPLOYEE],
                expires_delta=timedelta(seconds=-10),  # Already expired
            )

            # Decoding should raise HTTPException (within same context)
            with pytest.raises(HTTPException) as exc_info:
                decode_token(token)
            assert exc_info.value.status_code == 401

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_decode_malformed_token(self):
        """Test decoding a malformed token."""
        with pytest.raises(HTTPException) as exc_info:
            decode_token("notavalidjwt")
        assert exc_info.value.status_code == 401


class TestGetAuthenticatedUser:
    """Tests for get_authenticated_user dependency."""

    @pytest.mark.asyncio
    async def test_get_authenticated_user_success(self):
        """Test successful user authentication."""
        user_id = uuid4()
        org_id = uuid4()

        with patch("lms.app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test-secret-key"
            # Create a valid token
            token = create_access_token(
                user_id=user_id,
                organization_id=org_id,
                roles=[UserRole.EMPLOYEE],
            )

            # Mock credentials
            mock_credentials = MagicMock()
            mock_credentials.credentials = token

            # Mock user from DB
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_user.email = "test@example.com"
            mock_user.organization_id = org_id
            mock_user.status = UserStatus.ACTIVE

            # Mock DB session and repository
            mock_db = MagicMock()

            with patch("lms.app.core.security.UserRepository") as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo.get.return_value = mock_user
                mock_repo_class.return_value = mock_repo

                result = await get_authenticated_user(
                    credentials=mock_credentials,
                    db=mock_db,
                )

            assert result.user_id == user_id
            assert result.organization_id == org_id
            assert UserRole.EMPLOYEE in result.roles

    @pytest.mark.asyncio
    async def test_get_authenticated_user_not_found(self):
        """Test authentication fails when user not found."""
        user_id = uuid4()
        org_id = uuid4()

        with patch("lms.app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test-secret-key"
            # Create a valid token
            token = create_access_token(
                user_id=user_id,
                organization_id=org_id,
                roles=[UserRole.EMPLOYEE],
            )

            mock_credentials = MagicMock()
            mock_credentials.credentials = token
            mock_db = MagicMock()

            with patch("lms.app.core.security.UserRepository") as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo.get.return_value = None
                mock_repo.get_by_email.return_value = None
                mock_repo_class.return_value = mock_repo

                with pytest.raises(HTTPException) as exc_info:
                    await get_authenticated_user(
                        credentials=mock_credentials,
                        db=mock_db,
                    )

            assert exc_info.value.status_code == 403
            assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_authenticated_user_inactive(self):
        """Test authentication fails for inactive user."""
        user_id = uuid4()
        org_id = uuid4()

        with patch("lms.app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test-secret-key"
            # Create a valid token
            token = create_access_token(
                user_id=user_id,
                organization_id=org_id,
                roles=[UserRole.EMPLOYEE],
            )

            mock_credentials = MagicMock()
            mock_credentials.credentials = token

            mock_user = MagicMock()
            mock_user.id = user_id
            mock_user.email = "test@example.com"
            mock_user.organization_id = org_id
            mock_user.status = UserStatus.INACTIVE

            mock_db = MagicMock()

            with patch("lms.app.core.security.UserRepository") as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo.get.return_value = mock_user
                mock_repo_class.return_value = mock_repo

                with pytest.raises(HTTPException) as exc_info:
                    await get_authenticated_user(
                        credentials=mock_credentials,
                        db=mock_db,
                    )

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_authenticated_user_org_mismatch(self):
        """Test authentication fails when org_id doesn't match."""
        user_id = uuid4()
        token_org_id = uuid4()
        user_org_id = uuid4()  # Different org

        with patch("lms.app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test-secret-key"
            # Create a valid token
            token = create_access_token(
                user_id=user_id,
                organization_id=token_org_id,
                roles=[UserRole.EMPLOYEE],
            )

            mock_credentials = MagicMock()
            mock_credentials.credentials = token

            mock_user = MagicMock()
            mock_user.id = user_id
            mock_user.email = "test@example.com"
            mock_user.organization_id = user_org_id  # Different
            mock_user.status = UserStatus.ACTIVE

            mock_db = MagicMock()

            with patch("lms.app.core.security.UserRepository") as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo.get.return_value = mock_user
                mock_repo_class.return_value = mock_repo

                with pytest.raises(HTTPException) as exc_info:
                    await get_authenticated_user(
                        credentials=mock_credentials,
                        db=mock_db,
                    )

            assert exc_info.value.status_code == 403
            assert "organization" in exc_info.value.detail.lower()


class TestTokenPayloadAdvanced:
    """Additional tests for TokenPayload validation."""

    def test_token_payload_with_optional_fields(self):
        """Test TokenPayload with all optional fields."""
        payload = TokenPayload(
            sub="user-123",
            org_id="org-456",
            roles=["employee"],
            exp=int(datetime.now(timezone.utc).timestamp()) + 3600,
            oid="azure-oid-123",
        )
        assert payload.oid == "azure-oid-123"

    def test_token_payload_without_optional_fields(self):
        """Test TokenPayload without optional fields."""
        payload = TokenPayload(
            sub="user-123",
            org_id="org-456",
            roles=["employee"],
            exp=int(datetime.now(timezone.utc).timestamp()) + 3600,
        )
        assert payload.oid is None

    def test_token_payload_empty_roles(self):
        """Test TokenPayload with empty roles list."""
        payload = TokenPayload(
            sub="user-123",
            org_id="org-456",
            roles=[],
            exp=int(datetime.now(timezone.utc).timestamp()) + 3600,
        )
        assert payload.roles == []


class TestAuthenticatedUserAdvanced:
    """Additional tests for AuthenticatedUser model."""

    def test_authenticated_user_with_email(self):
        """Test AuthenticatedUser with email."""
        user = AuthenticatedUser(
            user_id=uuid4(),
            organization_id=uuid4(),
            roles=[UserRole.EMPLOYEE],
            email="test@example.com",
        )
        assert user.email == "test@example.com"

    def test_authenticated_user_without_email(self):
        """Test AuthenticatedUser without email."""
        user = AuthenticatedUser(
            user_id=uuid4(),
            organization_id=uuid4(),
            roles=[UserRole.EMPLOYEE],
            email=None,
        )
        assert user.email is None

    def test_authenticated_user_with_sso_subject(self):
        """Test AuthenticatedUser with SSO subject ID."""
        user = AuthenticatedUser(
            user_id=uuid4(),
            organization_id=uuid4(),
            roles=[UserRole.EMPLOYEE],
            sso_subject_id="azure-oid-123",
        )
        assert user.sso_subject_id == "azure-oid-123"
