"""Unit tests for calendar repository.

Tests HolidayCalendarRepository and HolidayRepository methods.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.repositories.calendar_repository import (
    HolidayCalendarRepository,
    HolidayRepository,
)


class TestHolidayCalendarRepository:
    """Tests for HolidayCalendarRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = HolidayCalendarRepository(mock_session)
        assert repo.session is mock_session

    def test_get_default_for_year_found(self):
        """Test get_default_for_year when calendar exists."""
        mock_session = MagicMock()
        mock_calendar = MagicMock()
        mock_calendar.year = 2024
        mock_session.execute.return_value.scalars.return_value.first.return_value = (
            mock_calendar
        )

        repo = HolidayCalendarRepository(mock_session)
        org_id = uuid4()
        result = repo.get_default_for_year(org_id, 2024)

        assert result is mock_calendar

    def test_get_default_for_year_not_found(self):
        """Test get_default_for_year when calendar doesn't exist."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        repo = HolidayCalendarRepository(mock_session)
        org_id = uuid4()
        result = repo.get_default_for_year(org_id, 2024)

        assert result is None


class TestHolidayRepository:
    """Tests for HolidayRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = HolidayRepository(mock_session)
        assert repo.session is mock_session

    def test_list_for_calendar(self):
        """Test list_for_calendar returns holidays."""
        mock_session = MagicMock()
        mock_holidays = [MagicMock(), MagicMock()]
        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            mock_holidays
        )

        repo = HolidayRepository(mock_session)
        calendar_id = uuid4()
        result = repo.list_for_calendar(calendar_id)

        assert result == mock_holidays
