"""Unit tests for notification repository.

Tests NotificationRepository and NotificationTemplateRepository methods.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.repositories.notification_repository import (
    NotificationRepository,
    NotificationTemplateRepository,
)


class TestNotificationTemplateRepository:
    """Tests for NotificationTemplateRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = NotificationTemplateRepository(mock_session)
        assert repo.session is mock_session

    def test_get_by_code_found(self):
        """Test get_by_code when template exists."""
        mock_session = MagicMock()
        mock_template = MagicMock()
        mock_template.code = "LEAVE_APPROVED"
        mock_session.execute.return_value.scalars.return_value.first.return_value = (
            mock_template
        )

        repo = NotificationTemplateRepository(mock_session)
        org_id = uuid4()
        result = repo.get_by_code(org_id, "LEAVE_APPROVED")

        assert result is mock_template

    def test_get_by_code_not_found(self):
        """Test get_by_code when template doesn't exist."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        repo = NotificationTemplateRepository(mock_session)
        org_id = uuid4()
        result = repo.get_by_code(org_id, "NONEXISTENT")

        assert result is None

    def test_get_by_code_global_template(self):
        """Test get_by_code for global template (no org)."""
        mock_session = MagicMock()
        mock_template = MagicMock()
        mock_session.execute.return_value.scalars.return_value.first.return_value = (
            mock_template
        )

        repo = NotificationTemplateRepository(mock_session)
        result = repo.get_by_code(None, "GLOBAL_TEMPLATE")

        assert result is mock_template


class TestNotificationRepository:
    """Tests for NotificationRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = NotificationRepository(mock_session)
        assert repo.session is mock_session

    def test_list_for_user(self):
        """Test list_for_user returns all notifications for user."""
        mock_session = MagicMock()
        mock_notifications = [MagicMock(), MagicMock(), MagicMock()]
        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            mock_notifications
        )

        repo = NotificationRepository(mock_session)
        user_id = uuid4()
        result = repo.list_for_user(user_id)

        assert result == mock_notifications
        assert len(result) == 3

    def test_list_for_user_with_pagination(self):
        """Test list_for_user with custom pagination."""
        mock_session = MagicMock()
        mock_notifications = [MagicMock()]
        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            mock_notifications
        )

        repo = NotificationRepository(mock_session)
        user_id = uuid4()
        result = repo.list_for_user(user_id, limit=10, offset=5)

        assert result == mock_notifications
