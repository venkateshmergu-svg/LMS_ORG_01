"""Unit tests for base repository."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from lms.app.core.exceptions import EntityNotFoundException
from lms.app.repositories.base import MAX_QUERY_LIMIT, BaseRepository


class FakeAuditContext:
    """Fake audit context."""

    def __init__(self):
        self.user_id = uuid4()
        self.correlation_id = str(uuid4())


class TestBaseRepository:
    """Tests for BaseRepository base class."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock SQLAlchemy session."""
        session = MagicMock()
        return session

    @pytest.fixture
    def mock_model_class(self):
        """Create a mock SQLAlchemy model class."""
        model_class = MagicMock()
        model_class.__name__ = "FakeModel"
        return model_class

    @pytest.fixture
    def repo(self, mock_session, mock_model_class):
        """Create a BaseRepository instance without audit."""
        return BaseRepository(mock_session, mock_model_class, audit_repo=None)

    # -------------------------------------------------------------------------
    # get() tests
    # -------------------------------------------------------------------------
    def test_get_returns_entity_when_found(self, repo, mock_session, mock_model_class):
        """get() should return entity when found."""
        entity_id = uuid4()
        expected = MagicMock()
        mock_session.get.return_value = expected

        result = repo.get(entity_id)

        assert result == expected
        mock_session.get.assert_called_once_with(mock_model_class, entity_id)

    def test_get_returns_none_when_not_found(self, repo, mock_session):
        """get() should return None when entity not found."""
        mock_session.get.return_value = None

        result = repo.get(uuid4())

        assert result is None

    # -------------------------------------------------------------------------
    # get_required() tests
    # -------------------------------------------------------------------------
    def test_get_required_returns_entity_when_found(self, repo, mock_session):
        """get_required() should return entity when found."""
        entity_id = uuid4()
        expected = MagicMock()
        mock_session.get.return_value = expected

        result = repo.get_required(entity_id)

        assert result == expected

    def test_get_required_raises_when_not_found(self, repo, mock_session):
        """get_required() should raise EntityNotFoundException when not found."""
        mock_session.get.return_value = None
        entity_id = uuid4()

        with pytest.raises(EntityNotFoundException) as exc_info:
            repo.get_required(entity_id)

        assert "FakeModel" in str(exc_info.value)


class TestMaxQueryLimit:
    """Tests for MAX_QUERY_LIMIT constant."""

    def test_max_limit_is_defined(self):
        """MAX_QUERY_LIMIT should be defined."""
        assert MAX_QUERY_LIMIT > 0

    def test_max_limit_is_reasonable(self):
        """MAX_QUERY_LIMIT should be a reasonable value."""
        assert MAX_QUERY_LIMIT == 1000
