"""Unit tests for security module."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from lms.app.core.enums import UserRole
from lms.app.core.security import (
    AuthenticatedUser,
    TokenPayload,
    decode_token,
)


class TestTokenPayload:
    """Tests for TokenPayload model."""

    def test_create_token_payload_required_fields(self):
        """TokenPayload should accept required fields."""
        payload = TokenPayload(
            sub="user@example.com",
            roles=["EMPLOYEE"],
            org_id=str(uuid4()),
        )

        assert payload.sub == "user@example.com"
        assert payload.roles == ["EMPLOYEE"]
        assert payload.oid is None  # optional
        assert payload.exp is None  # optional

    def test_create_token_payload_all_fields(self):
        """TokenPayload should accept all fields."""
        org_id = str(uuid4())
        exp_time = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())

        payload = TokenPayload(
            sub="user@example.com",
            roles=["EMPLOYEE", "MANAGER"],
            org_id=org_id,
            oid="azure-object-id-123",
            exp=exp_time,
        )

        assert payload.oid == "azure-object-id-123"
        assert payload.exp == exp_time


class TestAuthenticatedUser:
    """Tests for AuthenticatedUser model."""

    def test_create_authenticated_user(self):
        """AuthenticatedUser should hold authentication context."""
        user_id = uuid4()
        org_id = uuid4()

        user = AuthenticatedUser(
            user_id=user_id,
            email="user@example.com",
            organization_id=org_id,
            roles=[UserRole.EMPLOYEE],
        )

        assert user.user_id == user_id
        assert user.email == "user@example.com"
        assert user.organization_id == org_id
        assert UserRole.EMPLOYEE in user.roles

    def test_create_authenticated_user_without_optional_fields(self):
        """AuthenticatedUser should work without optional fields."""
        user = AuthenticatedUser(
            user_id=uuid4(),
            organization_id=uuid4(),
            roles=[UserRole.EMPLOYEE],
        )

        assert user.email is None
        assert user.sso_subject_id is None


class TestDecodeToken:
    """Tests for decode_token function."""

    @patch("lms.app.core.security.get_settings")
    @patch("lms.app.core.security.jwt.decode")
    def test_decode_valid_token(self, mock_jwt_decode, mock_get_settings):
        """decode_token should decode a valid JWT."""
        org_id = str(uuid4())
        mock_get_settings.return_value.SECRET_KEY = "test-secret"
        mock_jwt_decode.return_value = {
            "sub": "user@example.com",
            "roles": ["EMPLOYEE"],
            "org_id": org_id,
        }

        result = decode_token("valid.jwt.token")

        assert result.sub == "user@example.com"
        assert result.roles == ["EMPLOYEE"]
        assert result.org_id == org_id

    @patch("lms.app.core.security.get_settings")
    @patch("lms.app.core.security.jwt.decode")
    def test_decode_expired_token_raises(self, mock_jwt_decode, mock_get_settings):
        """decode_token should raise for expired tokens."""
        mock_get_settings.return_value.SECRET_KEY = "test-secret"
        # Set exp to past timestamp
        past_exp = int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp())
        mock_jwt_decode.return_value = {
            "sub": "user@example.com",
            "roles": ["EMPLOYEE"],
            "org_id": str(uuid4()),
            "exp": past_exp,
        }

        with pytest.raises(HTTPException) as exc_info:
            decode_token("expired.jwt.token")

        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    @patch("lms.app.core.security.get_settings")
    @patch("lms.app.core.security.jwt.decode")
    def test_decode_token_with_invalid_claims(self, mock_jwt_decode, mock_get_settings):
        """decode_token should raise for invalid claims."""
        from pydantic import ValidationError

        mock_get_settings.return_value.SECRET_KEY = "test-secret"
        # Missing required fields
        mock_jwt_decode.return_value = {
            "sub": "user@example.com",
            # Missing "roles" and "org_id"
        }

        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid.claims.token")

        assert exc_info.value.status_code == 401
        assert "invalid token claims" in exc_info.value.detail.lower()

    @patch("lms.app.core.security.get_settings")
    @patch("lms.app.core.security.jwt.decode")
    def test_decode_token_with_jwt_error(self, mock_jwt_decode, mock_get_settings):
        """decode_token should raise for JWT decode errors."""
        from jose import JWTError

        mock_get_settings.return_value.SECRET_KEY = "test-secret"
        mock_jwt_decode.side_effect = JWTError("Invalid signature")

        with pytest.raises(HTTPException) as exc_info:
            decode_token("bad.signature.token")

        assert exc_info.value.status_code == 401
        assert "could not validate" in exc_info.value.detail.lower()

    @patch("lms.app.core.security.get_settings")
    @patch("lms.app.core.security.jwt.decode")
    def test_decode_token_uses_hs256(self, mock_jwt_decode, mock_get_settings):
        """decode_token should use HS256 algorithm."""
        mock_get_settings.return_value.SECRET_KEY = "test-secret"
        mock_jwt_decode.return_value = {
            "sub": "user@example.com",
            "roles": ["EMPLOYEE"],
            "org_id": str(uuid4()),
        }

        decode_token("some.jwt.token")

        # Verify HS256 was used
        call_args = mock_jwt_decode.call_args
        assert call_args[1]["algorithms"] == ["HS256"]
