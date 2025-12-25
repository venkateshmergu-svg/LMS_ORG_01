"""Comprehensive tests for user repository.

Tests UserRepository, OrganizationRepository, DepartmentRepository.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.core.exceptions import DuplicateEntityException, EntityNotFoundException
from lms.app.repositories.audit_context import AuditContext
from lms.app.repositories.user_repository import (
    DepartmentRepository,
    OrganizationRepository,
    UserRepository,
)


def make_audit_ctx() -> AuditContext:
    """Create a test audit context."""
    return AuditContext(
        actor_id=uuid4(),
        actor_type="user",
        organization_id=uuid4(),
    )


class TestOrganizationRepository:
    """Tests for OrganizationRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = OrganizationRepository(mock_session)
        assert repo.session is mock_session

    def test_get_by_code_found(self):
        """Test get_by_code when organization exists."""
        mock_session = MagicMock()
        mock_org = MagicMock()
        mock_org.code = "ORG1"
        mock_session.execute.return_value.scalars.return_value.first.return_value = (
            mock_org
        )

        repo = OrganizationRepository(mock_session)
        result = repo.get_by_code("ORG1")

        assert result is mock_org

    def test_get_by_code_not_found(self):
        """Test get_by_code when organization doesn't exist."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        repo = OrganizationRepository(mock_session)
        result = repo.get_by_code("NONEXISTENT")

        assert result is None


class TestDepartmentRepository:
    """Tests for DepartmentRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = DepartmentRepository(mock_session)
        assert repo.session is mock_session

    def test_get_by_code_found(self):
        """Test get_by_code when department exists."""
        mock_session = MagicMock()
        mock_dept = MagicMock()
        mock_dept.code = "DEPT1"
        mock_session.execute.return_value.scalars.return_value.first.return_value = (
            mock_dept
        )

        repo = DepartmentRepository(mock_session)
        org_id = uuid4()
        result = repo.get_by_code(org_id, "DEPT1")

        assert result is mock_dept

    def test_get_by_code_not_found(self):
        """Test get_by_code when department doesn't exist."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        repo = DepartmentRepository(mock_session)
        org_id = uuid4()
        result = repo.get_by_code(org_id, "NONEXISTENT")

        assert result is None


class TestUserRepository:
    """Tests for UserRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = UserRepository(mock_session)
        assert repo.session is mock_session

    def test_get_by_email_found(self):
        """Test get_by_email when user exists."""
        mock_session = MagicMock()
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_session.execute.return_value.scalars.return_value.first.return_value = (
            mock_user
        )

        repo = UserRepository(mock_session)
        result = repo.get_by_email("test@example.com")

        assert result is mock_user

    def test_get_by_email_not_found(self):
        """Test get_by_email when user doesn't exist."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        repo = UserRepository(mock_session)
        result = repo.get_by_email("nonexistent@example.com")

        assert result is None

    def test_get_by_employee_id_found(self):
        """Test get_by_employee_id when user exists."""
        mock_session = MagicMock()
        mock_user = MagicMock()
        mock_user.employee_id = "EMP001"
        mock_session.execute.return_value.scalars.return_value.first.return_value = (
            mock_user
        )

        repo = UserRepository(mock_session)
        result = repo.get_by_employee_id("EMP001")

        assert result is mock_user

    def test_get_by_employee_id_not_found(self):
        """Test get_by_employee_id when user doesn't exist."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        repo = UserRepository(mock_session)
        result = repo.get_by_employee_id("NONEXISTENT")

        assert result is None

    def test_create_user_success(self):
        """Test successful user creation."""
        mock_session = MagicMock()
        mock_audit_repo = MagicMock()

        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.email = "new@example.com"
        mock_user.employee_id = "EMP_NEW"

        # No existing user with same email or employee_id
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        ctx = make_audit_ctx()

        repo = UserRepository(mock_session, audit_repo=mock_audit_repo)
        result = repo.create_user(mock_user, ctx=ctx)

        mock_session.add.assert_called_once_with(mock_user)
        assert result is mock_user

    def test_create_user_duplicate_email(self):
        """Test user creation fails with duplicate email."""
        mock_session = MagicMock()

        mock_existing_user = MagicMock()
        mock_existing_user.email = "existing@example.com"

        mock_new_user = MagicMock()
        mock_new_user.email = "existing@example.com"
        mock_new_user.employee_id = "EMP_NEW"

        # Return existing user for email check
        mock_session.execute.return_value.scalars.return_value.first.return_value = (
            mock_existing_user
        )

        ctx = make_audit_ctx()

        repo = UserRepository(mock_session)
        with pytest.raises(DuplicateEntityException) as exc_info:
            repo.create_user(mock_new_user, ctx=ctx)

        assert "email" in str(exc_info.value)

    def test_create_user_duplicate_employee_id(self):
        """Test user creation fails with duplicate employee_id."""
        mock_session = MagicMock()

        mock_new_user = MagicMock()
        mock_new_user.email = "new@example.com"
        mock_new_user.employee_id = "EMP_EXISTING"

        # First call (email check) returns None, second call (employee_id check) returns existing
        mock_existing = MagicMock()
        mock_session.execute.return_value.scalars.return_value.first.side_effect = [
            None,
            mock_existing,
        ]

        ctx = make_audit_ctx()

        repo = UserRepository(mock_session)
        with pytest.raises(DuplicateEntityException) as exc_info:
            repo.create_user(mock_new_user, ctx=ctx)

        assert "employee_id" in str(exc_info.value)

    def test_set_manager_success(self):
        """Test successful manager assignment."""
        mock_session = MagicMock()
        mock_audit_repo = MagicMock()

        user_id = uuid4()
        manager_id = uuid4()

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.manager_id = None

        mock_session.get.return_value = mock_user

        ctx = make_audit_ctx()

        repo = UserRepository(mock_session, audit_repo=mock_audit_repo)
        result = repo.set_manager(user_id, manager_id, ctx=ctx)

        assert result.manager_id == manager_id

    def test_set_manager_clear(self):
        """Test clearing manager assignment."""
        mock_session = MagicMock()

        user_id = uuid4()

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.manager_id = uuid4()

        mock_session.get.return_value = mock_user

        ctx = make_audit_ctx()

        repo = UserRepository(mock_session)
        result = repo.set_manager(user_id, None, ctx=ctx)

        assert result.manager_id is None

    def test_set_manager_user_not_found(self):
        """Test set_manager fails when user not found."""
        mock_session = MagicMock()
        mock_session.get.return_value = None

        user_id = uuid4()
        manager_id = uuid4()

        ctx = make_audit_ctx()

        repo = UserRepository(mock_session)
        with pytest.raises(EntityNotFoundException):
            repo.set_manager(user_id, manager_id, ctx=ctx)
