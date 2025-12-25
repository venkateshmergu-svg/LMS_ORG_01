"""Unit tests for auth endpoint helpers.

Tests _dev_user_from_code and token generation/exchange helpers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.api.v1.endpoints.auth import (
    MeResponse,
    RefreshRequest,
    TokenResponse,
    _dev_user_from_code,
    _generate_employee_id,
)
from lms.app.core.enums import UserRole


class TestDevUserFromCode:
    """Tests for _dev_user_from_code helper."""

    def test_dev_code_returns_system_admin(self):
        """Test 'dev' code returns alice as system admin."""
        email, first, last, roles = _dev_user_from_code("dev")
        assert email == "alice@example.com"
        assert first == "Alice"
        assert last == "Doe"
        assert roles == [UserRole.SYSTEM_ADMIN]

    def test_invalid_code_returns_default(self):
        """Test invalid code returns alice as system admin."""
        email, first, last, roles = _dev_user_from_code("invalid")
        assert email == "alice@example.com"
        assert roles == [UserRole.SYSTEM_ADMIN]

    def test_dev_employee_preset(self):
        """Test dev:employee returns employee user."""
        email, first, last, roles = _dev_user_from_code("dev:employee")
        assert email == "eve.employee@example.com"
        assert first == "Eve"
        assert last == "Employee"
        assert roles == [UserRole.EMPLOYEE]

    def test_dev_manager_preset(self):
        """Test dev:manager returns manager user."""
        email, first, last, roles = _dev_user_from_code("dev:manager")
        assert email == "mike.manager@example.com"
        assert first == "Mike"
        assert last == "Manager"
        assert roles == [UserRole.MANAGER]

    def test_dev_hr_preset(self):
        """Test dev:hr returns HR admin user."""
        email, first, last, roles = _dev_user_from_code("dev:hr")
        assert email == "helen.hr@example.com"
        assert first == "Helen"
        assert last == "HR"
        assert roles == [UserRole.HR_ADMIN]

    def test_dev_auditor_preset(self):
        """Test dev:auditor returns auditor user."""
        email, first, last, roles = _dev_user_from_code("dev:auditor")
        assert email == "andy.auditor@example.com"
        assert first == "Andy"
        assert last == "Auditor"
        assert roles == [UserRole.AUDITOR]

    def test_dev_sysadmin_preset(self):
        """Test dev:sysadmin returns system admin."""
        email, first, last, roles = _dev_user_from_code("dev:sysadmin")
        assert email == "admin@example.com"
        assert first == "System"
        assert last == "Admin"
        assert roles == [UserRole.SYSTEM_ADMIN]

    def test_dev_alice_preset(self):
        """Test dev:alice returns alice user."""
        email, first, last, roles = _dev_user_from_code("dev:alice")
        assert email == "alice@example.com"
        assert first == "Alice"
        assert last == "Doe"
        assert roles == [UserRole.SYSTEM_ADMIN]

    def test_dev_custom_email(self):
        """Test dev:<email> creates custom employee user."""
        email, first, last, roles = _dev_user_from_code("dev:john.smith@company.com")
        assert email == "john.smith@company.com"
        assert first == "John"
        assert last == "Smith"
        assert roles == [UserRole.EMPLOYEE]

    def test_dev_custom_email_simple(self):
        """Test dev:<simple_email> creates custom employee user."""
        email, first, last, roles = _dev_user_from_code("dev:user@test.com")
        assert email == "user@test.com"
        assert first == "User"
        assert last == "User"  # No period in local part
        assert roles == [UserRole.EMPLOYEE]

    def test_dev_unknown_selector_fallback(self):
        """Test unknown selector falls back to alice."""
        email, first, last, roles = _dev_user_from_code("dev:unknown")
        assert email == "alice@example.com"
        assert roles == [UserRole.SYSTEM_ADMIN]


class TestGenerateEmployeeId:
    """Tests for _generate_employee_id helper."""

    def test_generates_base_id(self):
        """Test basic employee ID generation."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        result = _generate_employee_id(mock_db, "john.doe@example.com")
        assert result.startswith("DEV_")
        assert "JOHN_DOE" in result or "JOHN" in result

    def test_handles_conflict_with_suffix(self):
        """Test employee ID generation with conflict."""
        mock_db = MagicMock()
        mock_result_exists = MagicMock()
        mock_result_exists.scalars.return_value.first.return_value = (
            MagicMock()
        )  # Exists
        mock_result_none = MagicMock()
        mock_result_none.scalars.return_value.first.return_value = None  # Doesn't exist

        mock_db.execute.side_effect = [mock_result_exists, mock_result_none]

        result = _generate_employee_id(mock_db, "test@example.com")
        assert "_2" in result or result.endswith("2")


class TestResponseModels:
    """Tests for Pydantic response models."""

    def test_token_response_model(self):
        """Test TokenResponse model."""
        response = TokenResponse(
            access_token="abc123",
            refresh_token="refresh456",
        )
        assert response.access_token == "abc123"
        assert response.refresh_token == "refresh456"
        assert response.token_type == "bearer"

    def test_me_response_model(self):
        """Test MeResponse model."""
        response = MeResponse(
            id="user-123",
            email="test@example.com",
            full_name="Test User",
            roles=["employee", "manager"],
        )
        assert response.id == "user-123"
        assert response.email == "test@example.com"
        assert response.full_name == "Test User"
        assert "employee" in response.roles

    def test_refresh_request_model(self):
        """Test RefreshRequest model."""
        request = RefreshRequest(refresh_token="old_token")
        assert request.refresh_token == "old_token"
