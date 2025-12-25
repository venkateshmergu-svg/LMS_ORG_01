"""Unit tests for Celery worker tasks."""

from datetime import date
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import pytest


class TestAccrualTasks:
    """Tests for accrual tasks."""

    @patch("lms.app.workers.tasks.accrual.SessionLocal")
    @patch("lms.app.workers.tasks.accrual.AuditRepository")
    @patch("lms.app.workers.tasks.accrual.LeavePolicyRepository")
    @patch("lms.app.workers.tasks.accrual.PolicyAssignmentRepository")
    @patch("lms.app.workers.tasks.accrual.LeaveBalanceRepository")
    @patch("lms.app.workers.tasks.accrual.AccrualScheduleRepository")
    @patch("lms.app.workers.tasks.accrual.PolicyEngine")
    def test_run_policy_accrual_returns_status(
        self,
        mock_policy_engine,
        mock_schedule_repo,
        mock_balance_repo,
        mock_assignment_repo,
        mock_policy_repo,
        mock_audit_repo,
        mock_session_local,
    ):
        """run_policy_accrual should return status dict."""
        # Setup
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        policy_id = str(uuid4())
        on_date = "2024-01-15"

        # Import and run task
        from lms.app.workers.tasks.accrual import run_policy_accrual

        result = run_policy_accrual(policy_id, on_date)

        assert result["status"] == "ok"
        assert result["policy_id"] == policy_id
        assert result["on_date"] == on_date
        mock_session.close.assert_called_once()

    @patch("lms.app.workers.tasks.accrual.SessionLocal")
    @patch("lms.app.workers.tasks.accrual.AuditRepository")
    @patch("lms.app.workers.tasks.accrual.LeavePolicyRepository")
    @patch("lms.app.workers.tasks.accrual.PolicyAssignmentRepository")
    @patch("lms.app.workers.tasks.accrual.LeaveBalanceRepository")
    @patch("lms.app.workers.tasks.accrual.AccrualScheduleRepository")
    @patch("lms.app.workers.tasks.accrual.PolicyEngine")
    def test_run_policy_accrual_closes_session_on_error(
        self,
        mock_policy_engine,
        mock_schedule_repo,
        mock_balance_repo,
        mock_assignment_repo,
        mock_policy_repo,
        mock_audit_repo,
        mock_session_local,
    ):
        """run_policy_accrual should close session even on error."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_audit_repo.side_effect = Exception("DB Error")

        from lms.app.workers.tasks.accrual import run_policy_accrual

        with pytest.raises(Exception):
            run_policy_accrual(str(uuid4()), "2024-01-15")

        mock_session.close.assert_called_once()


class TestNotificationTasks:
    """Tests for notification tasks."""

    @patch("lms.app.workers.tasks.notifications.SessionLocal")
    @patch("lms.app.workers.tasks.notifications.AuditRepository")
    @patch("lms.app.workers.tasks.notifications.NotificationRepository")
    def test_send_pending_notifications_returns_status(
        self, mock_notification_repo, mock_audit_repo, mock_session_local
    ):
        """send_pending_notifications should return status dict."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        from lms.app.workers.tasks.notifications import send_pending_notifications

        result = send_pending_notifications()

        assert result["status"] == "ok"
        mock_session.close.assert_called_once()

    @patch("lms.app.workers.tasks.notifications.SessionLocal")
    @patch("lms.app.workers.tasks.notifications.AuditRepository")
    @patch("lms.app.workers.tasks.notifications.NotificationRepository")
    def test_send_pending_notifications_closes_session_on_error(
        self, mock_notification_repo, mock_audit_repo, mock_session_local
    ):
        """send_pending_notifications should close session on error."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_audit_repo.side_effect = Exception("DB Error")

        from lms.app.workers.tasks.notifications import send_pending_notifications

        with pytest.raises(Exception):
            send_pending_notifications()

        mock_session.close.assert_called_once()


class TestIntegrationTasks:
    """Tests for integration tasks."""

    @patch("lms.app.workers.tasks.integrations.SessionLocal")
    @patch("lms.app.workers.tasks.integrations.AuditRepository")
    @patch("lms.app.workers.tasks.integrations.HRISSyncService")
    @patch("lms.app.workers.tasks.integrations.StubHRISAdapter")
    def test_sync_hris_task_returns_result(
        self, mock_stub_adapter, mock_sync_service, mock_audit_repo, mock_session_local
    ):
        """sync_hris_task should call sync service and return result."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_sync_service.return_value.sync.return_value = {"synced": 10}

        from lms.app.workers.tasks.integrations import sync_hris_task

        result = sync_hris_task()

        assert result == {"synced": 10}
        mock_session.close.assert_called_once()

    @patch("lms.app.workers.tasks.integrations.SessionLocal")
    @patch("lms.app.workers.tasks.integrations.AuditRepository")
    @patch("lms.app.workers.tasks.integrations.HRISSyncService")
    @patch("lms.app.workers.tasks.integrations.StubHRISAdapter")
    def test_sync_hris_task_closes_session_on_error(
        self, mock_stub_adapter, mock_sync_service, mock_audit_repo, mock_session_local
    ):
        """sync_hris_task should close session on error."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_sync_service.return_value.sync.side_effect = Exception("Sync failed")

        from lms.app.workers.tasks.integrations import sync_hris_task

        with pytest.raises(Exception):
            sync_hris_task()

        mock_session.close.assert_called_once()

    @patch("lms.app.workers.tasks.integrations.SessionLocal")
    @patch("lms.app.workers.tasks.integrations.AuditRepository")
    @patch("lms.app.workers.tasks.integrations.PayrollExportService")
    @patch("lms.app.workers.tasks.integrations.StubPayrollAdapter")
    def test_export_payroll_task_returns_result(
        self,
        mock_stub_adapter,
        mock_export_service,
        mock_audit_repo,
        mock_session_local,
    ):
        """export_payroll_task should call export service and return result."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_export_service.return_value.export.return_value = {"exported": 5}

        from lms.app.workers.tasks.integrations import export_payroll_task

        result = export_payroll_task("2024-01-01", "2024-01-31")

        assert result == {"exported": 5}
        mock_session.close.assert_called_once()

    @patch("lms.app.workers.tasks.integrations.SessionLocal")
    @patch("lms.app.workers.tasks.integrations.AuditRepository")
    @patch("lms.app.workers.tasks.integrations.PayrollExportService")
    @patch("lms.app.workers.tasks.integrations.StubPayrollAdapter")
    def test_export_payroll_task_parses_dates(
        self,
        mock_stub_adapter,
        mock_export_service,
        mock_audit_repo,
        mock_session_local,
    ):
        """export_payroll_task should parse ISO date strings."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_export_service.return_value.export.return_value = {}

        from lms.app.workers.tasks.integrations import export_payroll_task

        export_payroll_task("2024-06-01", "2024-06-30")

        # Verify export was called with date objects
        call_kwargs = mock_export_service.return_value.export.call_args[1]
        assert call_kwargs["start_date"] == date(2024, 6, 1)
        assert call_kwargs["end_date"] == date(2024, 6, 30)

    @patch("lms.app.workers.tasks.integrations.SessionLocal")
    @patch("lms.app.workers.tasks.integrations.AuditRepository")
    @patch("lms.app.workers.tasks.integrations.PayrollExportService")
    @patch("lms.app.workers.tasks.integrations.StubPayrollAdapter")
    def test_export_payroll_task_closes_session_on_error(
        self,
        mock_stub_adapter,
        mock_export_service,
        mock_audit_repo,
        mock_session_local,
    ):
        """export_payroll_task should close session on error."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_export_service.return_value.export.side_effect = Exception("Export failed")

        from lms.app.workers.tasks.integrations import export_payroll_task

        with pytest.raises(Exception):
            export_payroll_task("2024-01-01", "2024-01-31")

        mock_session.close.assert_called_once()
