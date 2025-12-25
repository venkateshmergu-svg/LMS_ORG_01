"""Unit tests for payroll export service."""

from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.integrations.payroll.adapter import PayrollExportResult, PayrollTransaction


class TestPayrollExportService:
    """Tests for PayrollExportService."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock SQLAlchemy session."""
        return MagicMock()

    @pytest.fixture
    def mock_leave_request(self):
        """Create a mock leave request."""
        req = MagicMock()
        req.id = uuid4()
        req.user_id = uuid4()
        req.start_date = date(2024, 1, 15)
        req.end_date = date(2024, 1, 17)
        req.total_days = 3.0

        # Mock user relationship (eager loaded)
        req.user = MagicMock()
        req.user.id = req.user_id
        req.user.employee_id = "EMP001"

        # Mock leave type
        req.leave_type = MagicMock()
        req.leave_type.code = "ANNUAL"

        return req

    @pytest.fixture
    def mock_adapter(self):
        """Create a mock payroll adapter."""
        adapter = MagicMock()
        adapter.__class__.__name__ = "TestPayrollAdapter"
        adapter.export_leave_transactions.return_value = PayrollExportResult(
            exported_count=1,
            succeeded=True,
            exported_at=datetime.now(timezone.utc),
            message="Export successful",
        )
        return adapter

    @pytest.fixture
    def audit_ctx(self):
        """Create a mock audit context."""
        ctx = MagicMock()
        ctx.actor_id = None
        ctx.actor_type = "scheduler"
        return ctx

    @patch("lms.app.integrations.payroll.export_service.AuditRepository")
    @patch("lms.app.integrations.payroll.export_service.LeaveRequestRepository")
    @patch("lms.app.integrations.payroll.export_service.UserRepository")
    @patch("lms.app.integrations.payroll.export_service.PayrollExportRepository")
    def test_export_with_no_approved_requests(
        self,
        mock_export_repo_cls,
        mock_user_repo_cls,
        mock_request_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_adapter,
        audit_ctx,
    ):
        """export should return zero when no approved requests."""
        mock_request_repo = MagicMock()
        mock_request_repo.list_approved_between.return_value = []
        mock_request_repo_cls.return_value = mock_request_repo

        from lms.app.integrations.payroll.export_service import PayrollExportService

        service = PayrollExportService(mock_session)
        result = service.export(
            adapter=mock_adapter,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            ctx=audit_ctx,
        )

        assert result["exported"] == 0
        assert result["skipped"] == 0
        mock_adapter.export_leave_transactions.assert_not_called()

    @patch("lms.app.integrations.payroll.export_service.AuditRepository")
    @patch("lms.app.integrations.payroll.export_service.LeaveRequestRepository")
    @patch("lms.app.integrations.payroll.export_service.UserRepository")
    @patch("lms.app.integrations.payroll.export_service.PayrollExportRepository")
    def test_export_with_approved_requests(
        self,
        mock_export_repo_cls,
        mock_user_repo_cls,
        mock_request_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_leave_request,
        mock_adapter,
        audit_ctx,
    ):
        """export should process approved requests."""
        mock_request_repo = MagicMock()
        mock_request_repo.list_approved_between.return_value = [mock_leave_request]
        mock_request_repo_cls.return_value = mock_request_repo

        mock_export_repo = MagicMock()
        mock_export_repo.mark_sent.return_value = MagicMock()  # Return a record
        mock_export_repo_cls.return_value = mock_export_repo

        from lms.app.integrations.payroll.export_service import PayrollExportService

        service = PayrollExportService(mock_session)
        result = service.export(
            adapter=mock_adapter,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            ctx=audit_ctx,
        )

        assert result["exported"] == 1
        assert result["succeeded"] is True
        mock_adapter.export_leave_transactions.assert_called_once()

    @patch("lms.app.integrations.payroll.export_service.AuditRepository")
    @patch("lms.app.integrations.payroll.export_service.LeaveRequestRepository")
    @patch("lms.app.integrations.payroll.export_service.UserRepository")
    @patch("lms.app.integrations.payroll.export_service.PayrollExportRepository")
    def test_to_transactions_uses_eager_loaded_user(
        self,
        mock_export_repo_cls,
        mock_user_repo_cls,
        mock_request_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_leave_request,
    ):
        """_to_transactions should use eager-loaded user relationship."""
        from lms.app.integrations.payroll.export_service import PayrollExportService

        service = PayrollExportService(mock_session)
        transactions = service._to_transactions([mock_leave_request])

        assert len(transactions) == 1
        tx = transactions[0]
        assert tx.employee_id == "EMP001"
        assert tx.leave_type_code == "ANNUAL"
        assert tx.days_used == 3.0

    @patch("lms.app.integrations.payroll.export_service.AuditRepository")
    @patch("lms.app.integrations.payroll.export_service.LeaveRequestRepository")
    @patch("lms.app.integrations.payroll.export_service.UserRepository")
    @patch("lms.app.integrations.payroll.export_service.PayrollExportRepository")
    def test_to_transactions_fetches_user_when_not_loaded(
        self,
        mock_export_repo_cls,
        mock_user_repo_cls,
        mock_request_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_leave_request,
    ):
        """_to_transactions should fetch user when relationship not loaded."""
        # Set user to None to trigger fallback
        mock_leave_request.user = None

        mock_user = MagicMock()
        mock_user.employee_id = "EMP002"
        mock_user_repo = MagicMock()
        mock_user_repo.get_required.return_value = mock_user
        mock_user_repo_cls.return_value = mock_user_repo

        from lms.app.integrations.payroll.export_service import PayrollExportService

        service = PayrollExportService(mock_session)
        transactions = service._to_transactions([mock_leave_request])

        assert transactions[0].employee_id == "EMP002"
        mock_user_repo.get_required.assert_called_once()

    @patch("lms.app.integrations.payroll.export_service.AuditRepository")
    @patch("lms.app.integrations.payroll.export_service.LeaveRequestRepository")
    @patch("lms.app.integrations.payroll.export_service.UserRepository")
    @patch("lms.app.integrations.payroll.export_service.PayrollExportRepository")
    def test_to_transactions_handles_no_leave_type(
        self,
        mock_export_repo_cls,
        mock_user_repo_cls,
        mock_request_repo_cls,
        mock_audit_repo_cls,
        mock_session,
        mock_leave_request,
    ):
        """_to_transactions should handle requests with no leave_type."""
        mock_leave_request.leave_type = None

        from lms.app.integrations.payroll.export_service import PayrollExportService

        service = PayrollExportService(mock_session)
        transactions = service._to_transactions([mock_leave_request])

        assert transactions[0].leave_type_code == "UNKNOWN"


class TestPayrollTransaction:
    """Tests for PayrollTransaction dataclass."""

    def test_create_transaction(self):
        """PayrollTransaction should hold transaction data."""
        tx = PayrollTransaction(
            leave_request_id=str(uuid4()),
            employee_id="EMP001",
            leave_type_code="ANNUAL",
            days_used=5.0,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 19),
        )

        assert tx.employee_id == "EMP001"
        assert tx.leave_type_code == "ANNUAL"
        assert tx.days_used == 5.0


class TestPayrollExportResult:
    """Tests for PayrollExportResult dataclass."""

    def test_create_result(self):
        """PayrollExportResult should hold export result data."""
        result = PayrollExportResult(
            exported_count=5,
            succeeded=True,
            exported_at=datetime.now(timezone.utc),
            message="Export complete",
        )

        assert result.succeeded is True
        assert result.exported_count == 5
        assert result.message == "Export complete"

    def test_create_failed_result(self):
        """PayrollExportResult should handle failure case."""
        result = PayrollExportResult(
            exported_count=0,
            succeeded=False,
            exported_at=datetime.now(timezone.utc),
            message="Connection failed",
        )

        assert result.succeeded is False
        assert result.exported_count == 0
