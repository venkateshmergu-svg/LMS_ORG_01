"""Base repository implementation.

Architectural constraint:
- No direct database access outside repositories.
- All mutations MUST emit audit events.

Repositories should not contain business logic; engines/services own domain rules.

Performance:
- MAX_LIMIT enforced to prevent unbounded queries
- Pagination support on all list operations
"""

from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.enums import AuditAction
from ..core.exceptions import EntityNotFoundException
from .audit_context import AuditContext
from .audit_repository import AuditRepository
from .utils import dict_diff, model_to_dict

TModel = TypeVar("TModel")

# Maximum limit for list queries to prevent memory issues
MAX_QUERY_LIMIT = 1000


class BaseRepository(Generic[TModel]):
    """Generic repository for CRUD access."""

    def __init__(
        self,
        session: Session,
        model: type[TModel],
        *,
        audit_repo: Optional["AuditRepository"] = None,
    ):
        self.session = session
        self.model = model
        self._audit_repo = audit_repo

    def get(self, entity_id: UUID) -> Optional[TModel]:
        return self.session.get(self.model, entity_id)

    def get_required(self, entity_id: UUID) -> TModel:
        entity = self.get(entity_id)
        if entity is None:
            raise EntityNotFoundException(self.model.__name__, entity_id)
        return entity

    def list(self, *, limit: int = 100, offset: int = 0) -> list[TModel]:
        """List entities with pagination.
        
        Args:
            limit: Maximum number of results (capped at MAX_QUERY_LIMIT)
            offset: Number of results to skip
            
        Returns:
            List of model instances
        """
        # Enforce maximum limit to prevent unbounded queries
        effective_limit = min(limit, MAX_QUERY_LIMIT)
        stmt = select(self.model).offset(offset).limit(effective_limit)
        return list(self.session.execute(stmt).scalars().all())
    
    def count(self) -> int:
        """Count total number of entities.
        
        Useful for pagination metadata.
        """
        from sqlalchemy import func
        stmt = select(func.count()).select_from(self.model)
        result = self.session.execute(stmt).scalar()
        return result or 0

    def add(self, entity: TModel, *, ctx: AuditContext, description: str | None = None) -> TModel:
        self.session.add(entity)
        self.session.flush()  # ensure PK is available

        self._emit_audit(
            action=AuditAction.CREATE,
            entity=entity,
            ctx=ctx,
            old_values=None,
            new_values=model_to_dict(entity),
            description=description,
        )
        return entity

    def update_fields(
        self,
        entity: TModel,
        fields: dict[str, Any],
        *,
        ctx: AuditContext,
        description: str | None = None,
    ) -> TModel:
        old_values = model_to_dict(entity)

        for key, value in fields.items():
            setattr(entity, key, value)

        self.session.flush()

        new_values = model_to_dict(entity)
        changes = dict_diff(old_values, new_values)
        self._emit_audit(
            action=AuditAction.UPDATE,
            entity=entity,
            ctx=ctx,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            description=description,
        )
        return entity

    def soft_delete(self, entity: TModel, *, ctx: AuditContext, description: str | None = None) -> TModel:
        old_values = model_to_dict(entity)

        if hasattr(entity, "is_deleted"):
            setattr(entity, "is_deleted", True)
        if hasattr(entity, "deleted_at"):
            from datetime import datetime, timezone

            setattr(entity, "deleted_at", datetime.now(timezone.utc))

        self.session.flush()

        new_values = model_to_dict(entity)
        changes = dict_diff(old_values, new_values)
        self._emit_audit(
            action=AuditAction.DELETE,
            entity=entity,
            ctx=ctx,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            description=description,
        )
        return entity

    def _emit_audit(
        self,
        *,
        action: AuditAction,
        entity: TModel,
        ctx: AuditContext,
        old_values: dict[str, Any] | None,
        new_values: dict[str, Any] | None,
        changes: dict[str, Any] | None = None,
        description: str | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> None:
        if self._audit_repo is None:
            return

        entity_id = getattr(entity, "id", None)
        if entity_id is None:
            return

        self._audit_repo.append(
            action=action,
            entity_type=self.model.__name__,
            entity_id=entity_id,
            ctx=ctx,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            description=description,
            extra_metadata=extra_metadata,
        )


