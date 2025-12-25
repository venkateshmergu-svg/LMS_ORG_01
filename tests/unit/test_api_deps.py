"""Unit tests for API dependencies."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.core.enums import UserRole
from lms.app.core.security import AuthenticatedUser
from lms.app.repositories import AuditContext


class TestGetAuditContext:
    """Tests for get_audit_context dependency."""

    @pytest.fixture
    def authenticated_user(self):
        """Create an authenticated user."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="user@example.com",
            organization_id=uuid4(),
            roles=[UserRole.EMPLOYEE],
        )

    def test_uses_authenticated_user_when_available(self, authenticated_user):
        """get_audit_context should use authenticated user when available."""
        from lms.app.api.deps import get_audit_context

        result = get_audit_context(
            x_actor_id=None,
            x_organization_id=None,
            x_request_id="req-123",
            x_session_id="sess-456",
            auth_user=authenticated_user,
        )

        assert result.actor_id == authenticated_user.user_id
        assert result.organization_id == authenticated_user.organization_id
        assert result.actor_type == "user"

    def test_falls_back_to_headers(self):
        """get_audit_context should fall back to headers without auth user."""
        from lms.app.api.deps import get_audit_context

        actor_id = uuid4()
        org_id = uuid4()

        result = get_audit_context(
            x_actor_id=str(actor_id),
            x_organization_id=str(org_id),
            x_request_id="req-123",
            x_session_id=None,
            auth_user=None,
        )

        assert result.actor_id == actor_id
        assert result.organization_id == org_id
        assert result.actor_type == "user"

    def test_system_actor_when_no_id(self):
        """get_audit_context should set actor_type to 'system' when no actor_id."""
        from lms.app.api.deps import get_audit_context

        result = get_audit_context(
            x_actor_id=None,
            x_organization_id=None,
            x_request_id=None,
            x_session_id=None,
            auth_user=None,
        )

        assert result.actor_id is None
        assert result.actor_type == "system"

    def test_includes_request_tracking_ids(self, authenticated_user):
        """get_audit_context should include request and session IDs."""
        from lms.app.api.deps import get_audit_context

        result = get_audit_context(
            x_actor_id=None,
            x_organization_id=None,
            x_request_id="req-xyz",
            x_session_id="sess-abc",
            auth_user=authenticated_user,
        )

        assert result.request_id == "req-xyz"
        assert result.session_id == "sess-abc"


class TestEngineDependencies:
    """Tests for engine dependency factories."""

    @pytest.fixture
    def mock_uow(self):
        """Create a mock UnitOfWork."""
        uow = MagicMock()
        uow.session = MagicMock()
        return uow

    def test_get_audit_engine(self, mock_uow):
        """get_audit_engine should create AuditEngine with session."""
        from lms.app.api.deps import get_audit_engine

        with patch("lms.app.api.deps.AuditEngine") as mock_engine_cls:
            get_audit_engine(uow=mock_uow)
            mock_engine_cls.assert_called_once_with(mock_uow.session)

    def test_get_user_engine(self, mock_uow):
        """get_user_engine should create UserEngine with repositories."""
        from lms.app.api.deps import get_user_engine

        with patch("lms.app.api.deps.UserEngine") as mock_engine_cls:
            with patch("lms.app.api.deps.AuditRepository"):
                with patch("lms.app.api.deps.UserRepository"):
                    get_user_engine(uow=mock_uow)
                    mock_engine_cls.assert_called_once()
