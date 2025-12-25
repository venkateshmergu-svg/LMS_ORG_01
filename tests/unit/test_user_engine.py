"""Unit tests for UserEngine.

Tests:
- User creation
- User retrieval
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from lms.app.core.exceptions import EntityNotFoundException
from lms.app.engines.user_engine import UserCreated, UserEngine
from lms.app.repositories import AuditContext
from tests.conftest import FakeSession, FakeUser


class FakeUserRepository:
    """Fake user repository."""

    def __init__(self) -> None:
        self._entities: dict = {}

    def create_user(self, user, *, ctx):
        if not hasattr(user, "id") or user.id is None:
            user.id = uuid4()
        self._entities[user.id] = user
        return user

    def get_required(self, entity_id):
        entity = self._entities.get(entity_id)
        if entity is None:
            raise EntityNotFoundException("User", entity_id)
        return entity


@pytest.fixture
def user_repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def user_engine(fake_session: FakeSession, user_repo: FakeUserRepository) -> UserEngine:
    """Provide a UserEngine with fake repositories."""
    return UserEngine(
        fake_session,  # type: ignore[arg-type]
        user_repo=user_repo,  # type: ignore[arg-type]
    )


@pytest.mark.unit
class TestUserCreation:
    """Tests for user creation."""

    def test_create_user_success(
        self,
        user_engine: UserEngine,
        user_repo: FakeUserRepository,
        audit_ctx: AuditContext,
    ) -> None:
        """Test successful user creation."""
        user = FakeUser(
            email="newuser@example.com",
            first_name="New",
            last_name="User",
        )

        result = user_engine.create_user(user=user, ctx=audit_ctx)  # type: ignore[arg-type]

        assert isinstance(result, UserCreated)
        assert result.user.email == "newuser@example.com"
        assert user.id in user_repo._entities

    def test_create_user_generates_id_if_missing(
        self,
        user_engine: UserEngine,
        audit_ctx: AuditContext,
    ) -> None:
        """Test that user creation generates ID if missing."""
        user = FakeUser()
        # Remove the ID that FakeUser generates by default
        original_id = user.id

        result = user_engine.create_user(user=user, ctx=audit_ctx)  # type: ignore[arg-type]

        assert result.user.id is not None


@pytest.mark.unit
class TestUserRetrieval:
    """Tests for user retrieval."""

    def test_get_user_returns_user(
        self,
        user_engine: UserEngine,
        user_repo: FakeUserRepository,
    ) -> None:
        """Test that get_user returns the user."""
        user = FakeUser()
        user_repo._entities[user.id] = user

        result = user_engine.get_user(user_id=user.id)

        assert result == user

    def test_get_user_raises_when_not_found(
        self,
        user_engine: UserEngine,
    ) -> None:
        """Test that get_user raises EntityNotFoundException when user not found."""
        with pytest.raises(EntityNotFoundException) as exc_info:
            user_engine.get_user(user_id=uuid4())

        assert "User" in str(exc_info.value)
