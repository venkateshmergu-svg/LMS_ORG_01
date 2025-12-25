"""Unit tests for workflow repository.

Tests WorkflowConfigurationRepository and WorkflowStepRepository methods.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from lms.app.repositories.workflow_repository import (
    DelegationRepository,
    WorkflowConfigurationRepository,
    WorkflowStepRepository,
)


class TestWorkflowConfigurationRepository:
    """Tests for WorkflowConfigurationRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = WorkflowConfigurationRepository(mock_session)
        assert repo.session is mock_session

    def test_list_active_for_org_found(self):
        """Test list_active_for_org when configurations exist."""
        mock_session = MagicMock()
        mock_configs = [MagicMock(), MagicMock()]
        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            mock_configs
        )

        repo = WorkflowConfigurationRepository(mock_session)
        org_id = uuid4()
        result = repo.list_active_for_org(org_id)

        assert result == mock_configs

    def test_list_active_for_org_empty(self):
        """Test list_active_for_org when no configurations exist."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []

        repo = WorkflowConfigurationRepository(mock_session)
        org_id = uuid4()
        result = repo.list_active_for_org(org_id)

        assert result == []

    def test_list_active_for_org_with_date(self):
        """Test list_active_for_org with specific date."""
        mock_session = MagicMock()
        mock_configs = [MagicMock()]
        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            mock_configs
        )

        repo = WorkflowConfigurationRepository(mock_session)
        org_id = uuid4()
        result = repo.list_active_for_org(org_id, on_date=datetime.now(timezone.utc))

        assert result == mock_configs


class TestWorkflowStepRepository:
    """Tests for WorkflowStepRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = WorkflowStepRepository(mock_session)
        assert repo.session is mock_session


class TestDelegationRepository:
    """Tests for DelegationRepository."""

    def test_init(self):
        """Test repository initialization."""
        mock_session = MagicMock()
        repo = DelegationRepository(mock_session)
        assert repo.session is mock_session
