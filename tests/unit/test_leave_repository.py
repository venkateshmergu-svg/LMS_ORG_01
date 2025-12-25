"""Unit tests for leave repository.

Tests LeaveRepository, LeaveBalanceRepository, etc.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.repositories.leave_repository import (
    LeaveBalanceRepository,
    LeavePolicyRepository,
    LeaveRequestRepository,
    LeaveTypeRepository,
)


class TestLeaveTypeRepository:
    """Tests for LeaveTypeRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = LeaveTypeRepository(mock_session)
        assert repo.session is mock_session

    def test_get_by_code_found(self):
        """Test get_by_code when type exists."""
        mock_session = MagicMock()
        mock_leave_type = MagicMock()
        mock_leave_type.code = "ANNUAL"
        mock_session.execute.return_value.scalars.return_value.first.return_value = (
            mock_leave_type
        )

        repo = LeaveTypeRepository(mock_session)
        org_id = uuid4()
        result = repo.get_by_code(org_id, "ANNUAL")

        assert result is mock_leave_type

    def test_get_by_code_not_found(self):
        """Test get_by_code when type doesn't exist."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        repo = LeaveTypeRepository(mock_session)
        org_id = uuid4()
        result = repo.get_by_code(org_id, "NONEXISTENT")

        assert result is None


class TestLeavePolicyRepository:
    """Tests for LeavePolicyRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = LeavePolicyRepository(mock_session)
        assert repo.session is mock_session

    def test_get_active_for_leave_type_found(self):
        """Test get_active_for_leave_type when policies exist."""
        mock_session = MagicMock()
        mock_policies = [MagicMock(), MagicMock()]
        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            mock_policies
        )

        repo = LeavePolicyRepository(mock_session)
        org_id = uuid4()
        type_id = uuid4()
        result = repo.get_active_for_leave_type(org_id, type_id)

        assert result == mock_policies

    def test_get_active_for_leave_type_empty(self):
        """Test get_active_for_leave_type when no policies exist."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []

        repo = LeavePolicyRepository(mock_session)
        org_id = uuid4()
        type_id = uuid4()
        result = repo.get_active_for_leave_type(org_id, type_id)

        assert result == []


class TestLeaveBalanceRepository:
    """Tests for LeaveBalanceRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = LeaveBalanceRepository(mock_session)
        assert repo.session is mock_session

    def test_get_current_balance_found(self):
        """Test get_current_balance when balance exists."""
        mock_session = MagicMock()
        mock_balance = MagicMock()
        mock_session.execute.return_value.scalars.return_value.first.return_value = (
            mock_balance
        )

        repo = LeaveBalanceRepository(mock_session)
        user_id = uuid4()
        type_id = uuid4()
        result = repo.get_current_balance(user_id, type_id, date(2024, 6, 15))

        assert result is mock_balance

    def test_get_current_balance_not_found(self):
        """Test get_current_balance when balance doesn't exist."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        repo = LeaveBalanceRepository(mock_session)
        user_id = uuid4()
        type_id = uuid4()
        result = repo.get_current_balance(user_id, type_id, date(2024, 6, 15))

        assert result is None


class TestLeaveRequestRepository:
    """Tests for LeaveRequestRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = LeaveRequestRepository(mock_session)
        assert repo.session is mock_session

    def test_find_overlaps_found(self):
        """Test find_overlaps when overlapping requests exist."""
        mock_session = MagicMock()
        mock_requests = [MagicMock()]
        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            mock_requests
        )

        repo = LeaveRequestRepository(mock_session)
        user_id = uuid4()
        result = repo.find_overlaps(user_id, date(2024, 1, 1), date(2024, 1, 5))

        assert result == mock_requests

    def test_find_overlaps_not_found(self):
        """Test find_overlaps when no overlapping requests."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []

        repo = LeaveRequestRepository(mock_session)
        user_id = uuid4()
        result = repo.find_overlaps(user_id, date(2024, 1, 1), date(2024, 1, 5))

        assert result == []

    def test_list_approved_between(self):
        """Test list_approved_between returns approved requests."""
        mock_session = MagicMock()
        mock_requests = [MagicMock(), MagicMock()]
        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            mock_requests
        )

        repo = LeaveRequestRepository(mock_session)
        result = repo.list_approved_between(date(2024, 1, 1), date(2024, 12, 31))

        assert result == mock_requests
