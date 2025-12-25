"""Unit tests for calendar integration service."""

from datetime import date
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest


class TestCalendarIntegrationService:
    """Tests for CalendarIntegrationService."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock SQLAlchemy session."""
        return MagicMock()

    @pytest.fixture
    def mock_request(self):
        """Create a mock leave request with user and leave_type."""
        req = MagicMock()
        req.id = uuid4()
        req.user_id = uuid4()
        req.start_date = date(2024, 1, 15)
        req.end_date = date(2024, 1, 17)
        req.total_days = 3

        # Mock user relationship
        req.user = MagicMock()
        req.user.id = req.user_id
        req.user.full_name = "John Doe"
        req.user.employee_id = "EMP001"

        # Mock leave_type relationship
        req.leave_type = MagicMock()
        req.leave_type.code = "ANNUAL"

        return req

    @patch("lms.app.integrations.calendar.service.AuditRepository")
    @patch("lms.app.integrations.calendar.service.LeaveRequestRepository")
    @patch("lms.app.integrations.calendar.service.UserRepository")
    def test_generate_events_returns_events_for_approved_requests(
        self,
        mock_user_repo_cls,
        mock_request_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_request,
    ):
        """generate_events should return calendar events for approved leaves."""
        # Setup
        mock_request_repo = MagicMock()
        mock_request_repo.list_approved_between.return_value = [mock_request]
        mock_request_repo_cls.return_value = mock_request_repo

        from lms.app.integrations.calendar.service import CalendarIntegrationService

        service = CalendarIntegrationService(mock_session)

        # Execute
        events = service.generate_events(date(2024, 1, 1), date(2024, 1, 31))

        # Verify
        assert len(events) == 1
        event = events[0]
        assert event["title"] == "John Doe on ANNUAL"
        assert event["user_employee_id"] == "EMP001"
        assert event["start_date"] == "2024-01-15"
        assert event["end_date"] == "2024-01-17"
        assert event["days"] == 3.0

    @patch("lms.app.integrations.calendar.service.AuditRepository")
    @patch("lms.app.integrations.calendar.service.LeaveRequestRepository")
    @patch("lms.app.integrations.calendar.service.UserRepository")
    def test_generate_events_handles_no_leave_type(
        self,
        mock_user_repo_cls,
        mock_request_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_request,
    ):
        """generate_events should handle requests without leave_type."""
        mock_request.leave_type = None

        mock_request_repo = MagicMock()
        mock_request_repo.list_approved_between.return_value = [mock_request]
        mock_request_repo_cls.return_value = mock_request_repo

        from lms.app.integrations.calendar.service import CalendarIntegrationService

        service = CalendarIntegrationService(mock_session)
        events = service.generate_events(date(2024, 1, 1), date(2024, 1, 31))

        assert events[0]["title"] == "John Doe on Leave"

    @patch("lms.app.integrations.calendar.service.AuditRepository")
    @patch("lms.app.integrations.calendar.service.LeaveRequestRepository")
    @patch("lms.app.integrations.calendar.service.UserRepository")
    def test_generate_events_fetches_user_when_not_loaded(
        self,
        mock_user_repo_cls,
        mock_request_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_request,
    ):
        """generate_events should fetch user when relationship not loaded."""
        # Set user to None to trigger fallback
        mock_request.user = None

        mock_user = MagicMock()
        mock_user.id = mock_request.user_id
        mock_user.full_name = "Jane Smith"
        mock_user.employee_id = "EMP002"

        mock_user_repo = MagicMock()
        mock_user_repo.get_required.return_value = mock_user
        mock_user_repo_cls.return_value = mock_user_repo

        mock_request_repo = MagicMock()
        mock_request_repo.list_approved_between.return_value = [mock_request]
        mock_request_repo_cls.return_value = mock_request_repo

        from lms.app.integrations.calendar.service import CalendarIntegrationService

        service = CalendarIntegrationService(mock_session)
        events = service.generate_events(date(2024, 1, 1), date(2024, 1, 31))

        assert events[0]["user_employee_id"] == "EMP002"
        mock_user_repo.get_required.assert_called_once()

    @patch("lms.app.integrations.calendar.service.AuditRepository")
    @patch("lms.app.integrations.calendar.service.LeaveRequestRepository")
    @patch("lms.app.integrations.calendar.service.UserRepository")
    def test_generate_events_returns_empty_when_no_approved(
        self,
        mock_user_repo_cls,
        mock_request_repo_cls,
        mock_audit_repo_cls,
        mock_session,
    ):
        """generate_events should return empty list when no approved requests."""
        mock_request_repo = MagicMock()
        mock_request_repo.list_approved_between.return_value = []
        mock_request_repo_cls.return_value = mock_request_repo

        from lms.app.integrations.calendar.service import CalendarIntegrationService

        service = CalendarIntegrationService(mock_session)
        events = service.generate_events(date(2024, 1, 1), date(2024, 1, 31))

        assert events == []

    @patch("lms.app.integrations.calendar.service.AuditRepository")
    @patch("lms.app.integrations.calendar.service.LeaveRequestRepository")
    @patch("lms.app.integrations.calendar.service.UserRepository")
    def test_generate_events_multiple_requests(
        self,
        mock_user_repo_cls,
        mock_request_repo_cls,
        mock_audit_repo_cls,
        mock_session,
    ):
        """generate_events should handle multiple requests."""
        requests = []
        for i in range(3):
            req = MagicMock()
            req.id = uuid4()
            req.user_id = uuid4()
            req.start_date = date(2024, 1, 10 + i)
            req.end_date = date(2024, 1, 12 + i)
            req.total_days = 2
            req.user = MagicMock()
            req.user.id = req.user_id
            req.user.full_name = f"User {i}"
            req.user.employee_id = f"EMP00{i}"
            req.leave_type = MagicMock()
            req.leave_type.code = "ANNUAL"
            requests.append(req)

        mock_request_repo = MagicMock()
        mock_request_repo.list_approved_between.return_value = requests
        mock_request_repo_cls.return_value = mock_request_repo

        from lms.app.integrations.calendar.service import CalendarIntegrationService

        service = CalendarIntegrationService(mock_session)
        events = service.generate_events(date(2024, 1, 1), date(2024, 1, 31))

        assert len(events) == 3
