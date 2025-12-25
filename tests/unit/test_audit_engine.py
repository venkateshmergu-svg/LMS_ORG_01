"""Unit tests for audit engine."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.engines.audit_engine import AuditEngine


class TestAuditEngine:
    """Tests for AuditEngine."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock SQLAlchemy session."""
        return MagicMock()

    @pytest.fixture
    def engine(self, mock_session):
        """Create an AuditEngine instance."""
        with patch("lms.app.engines.audit_engine.AuditRepository") as mock_repo_cls:
            mock_repo = MagicMock()
            mock_repo_cls.return_value = mock_repo
            engine = AuditEngine(mock_session)
            engine.audit_repo = mock_repo
            return engine

    def test_list_entity_events_calls_repository(self, engine):
        """list_entity_events should delegate to repository."""
        entity_id = uuid4()
        engine.audit_repo.list_for_entity.return_value = []

        result = engine.list_entity_events(
            entity_type="LeaveRequest", entity_id=entity_id, limit=50, offset=10
        )

        engine.audit_repo.list_for_entity.assert_called_once_with(
            entity_type="LeaveRequest",
            entity_id=entity_id,
            limit=50,
            offset=10,
        )

    def test_list_entity_events_uses_defaults(self, engine):
        """list_entity_events should use default limit and offset."""
        entity_id = uuid4()
        engine.audit_repo.list_for_entity.return_value = []

        engine.list_entity_events(entity_type="User", entity_id=entity_id)

        call_kwargs = engine.audit_repo.list_for_entity.call_args[1]
        assert call_kwargs["limit"] == 100
        assert call_kwargs["offset"] == 0

    def test_make_context_creates_audit_context(self, engine):
        """make_context should create an AuditContext."""
        actor_id = uuid4()
        org_id = uuid4()

        result = engine.make_context(
            actor_id=actor_id,
            actor_type="user",
            organization_id=org_id,
        )

        assert result.actor_id == actor_id
        assert result.actor_type == "user"
        assert result.organization_id == org_id

    def test_make_context_with_all_params(self, engine):
        """make_context should accept all optional parameters."""
        result = engine.make_context(
            actor_id=uuid4(),
            actor_type="system",
            organization_id=uuid4(),
            actor_ip="192.168.1.1",
            actor_user_agent="Mozilla/5.0",
            request_id="req-123",
            session_id="sess-456",
            extra={"key": "value"},
        )

        assert result.actor_ip == "192.168.1.1"
        assert result.actor_user_agent == "Mozilla/5.0"
        assert result.request_id == "req-123"
        assert result.session_id == "sess-456"

    def test_make_context_with_none_values(self, engine):
        """make_context should handle None values."""
        result = engine.make_context(
            actor_id=None,
            actor_type="scheduler",
        )

        assert result.actor_id is None
        assert result.actor_type == "scheduler"
