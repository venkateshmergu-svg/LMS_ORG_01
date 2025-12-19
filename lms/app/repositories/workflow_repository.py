"""Workflow repositories."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.workflow import (
    Delegation,
    WorkflowConfiguration,
    WorkflowStep,
    WorkflowStepConfiguration,
)
from .base import BaseRepository


class WorkflowConfigurationRepository(BaseRepository[WorkflowConfiguration]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, WorkflowConfiguration, audit_repo=audit_repo)

    def list_active_for_org(self, organization_id: UUID, on_date: Optional[datetime] = None) -> list[WorkflowConfiguration]:
        stmt = select(WorkflowConfiguration).where(
            WorkflowConfiguration.organization_id == organization_id,
            WorkflowConfiguration.is_active.is_(True),
        )
        if on_date is not None:
            stmt = stmt.where(WorkflowConfiguration.effective_from <= on_date).where(
                (WorkflowConfiguration.effective_to.is_(None)) | (WorkflowConfiguration.effective_to >= on_date)
            )
        stmt = stmt.order_by(WorkflowConfiguration.priority.desc())
        return list(self.session.execute(stmt).scalars().all())


class WorkflowStepConfigurationRepository(BaseRepository[WorkflowStepConfiguration]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, WorkflowStepConfiguration, audit_repo=audit_repo)


class WorkflowStepRepository(BaseRepository[WorkflowStep]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, WorkflowStep, audit_repo=audit_repo)


class DelegationRepository(BaseRepository[Delegation]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, Delegation, audit_repo=audit_repo)
