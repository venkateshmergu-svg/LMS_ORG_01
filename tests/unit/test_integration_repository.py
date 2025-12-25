"""Unit tests for integration repository.

Tests PayrollExportRepository methods.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.repositories.audit_context import AuditContext
from lms.app.repositories.integration_repository import PayrollExportRepository


def make_audit_ctx() -> AuditContext:
    """Create a test audit context."""
    return AuditContext(
        actor_id=uuid4(),
        actor_type="user",
        organization_id=uuid4(),
    )


class TestPayrollExportRepository:
    """Tests for PayrollExportRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = PayrollExportRepository(mock_session)
        assert repo.session is mock_session

    def test_get_by_key_found(self):
        """Test get_by_key when record exists."""
        mock_session = MagicMock()
        mock_record = MagicMock()
        mock_record.export_key = "EMP001-2024-01-01-2024-01-05"
        mock_session.execute.return_value.scalars.return_value.first.return_value = (
            mock_record
        )

        repo = PayrollExportRepository(mock_session)
        result = repo.get_by_key("EMP001-2024-01-01-2024-01-05")

        assert result is mock_record

    def test_get_by_key_not_found(self):
        """Test get_by_key when record doesn't exist."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        repo = PayrollExportRepository(mock_session)
        result = repo.get_by_key("nonexistent-key")

        assert result is None

    def test_mark_sent_creates_new_record(self):
        """Test mark_sent creates new record when doesn't exist."""
        mock_session = MagicMock()
        mock_audit_repo = MagicMock()

        # get_by_key returns None (no existing record)
        mock_session.execute.return_value.scalars.return_value.first.return_value = None

        ctx = make_audit_ctx()
        repo = PayrollExportRepository(mock_session, audit_repo=mock_audit_repo)

        result = repo.mark_sent(
            leave_request_id=uuid4(),
            employee_id="EMP001",
            leave_type_code="ANNUAL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
            adapter_name="stub",
            export_key="EMP001-2024-01-01-2024-01-05",
            exported_at=datetime.now(timezone.utc),
            ctx=ctx,
        )

        mock_session.add.assert_called_once()
        assert result is not None

    def test_mark_sent_returns_existing_record(self):
        """Test mark_sent returns existing record if found."""
        mock_session = MagicMock()

        mock_existing = MagicMock()
        mock_existing.export_key = "EMP001-2024-01-01-2024-01-05"
        mock_session.execute.return_value.scalars.return_value.first.return_value = (
            mock_existing
        )

        ctx = make_audit_ctx()
        repo = PayrollExportRepository(mock_session)

        result = repo.mark_sent(
            leave_request_id=uuid4(),
            employee_id="EMP001",
            leave_type_code="ANNUAL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
            adapter_name="stub",
            export_key="EMP001-2024-01-01-2024-01-05",
            exported_at=datetime.now(timezone.utc),
            ctx=ctx,
        )

        assert result is mock_existing
        mock_session.add.assert_not_called()
