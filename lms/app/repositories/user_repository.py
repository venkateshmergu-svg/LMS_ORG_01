"""User/organization repositories."""

from __future__ import annotations

from typing import Optional, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.exceptions import DuplicateEntityException
from ..models.user import Department, Organization, User
from .audit_context import AuditContext
from .base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, Organization, audit_repo=audit_repo)

    def get_by_code(self, code: str) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.code == code)
        return self.session.execute(stmt).scalars().first()


class DepartmentRepository(BaseRepository[Department]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, Department, audit_repo=audit_repo)


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session, *, audit_repo=None):
        super().__init__(session, User, audit_repo=audit_repo)

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return self.session.execute(stmt).scalars().first()

    def get_by_employee_id(self, employee_id: str) -> Optional[User]:
        stmt = select(User).where(User.employee_id == employee_id)
        return self.session.execute(stmt).scalars().first()

    def create_user(self, user: User, *, ctx: AuditContext) -> User:
        email = cast(str, user.email)
        employee_id = cast(str, user.employee_id)

        if self.get_by_email(email):
            raise DuplicateEntityException("User", "email", email)
        if self.get_by_employee_id(employee_id):
            raise DuplicateEntityException("User", "employee_id", employee_id)
        return self.add(user, ctx=ctx)

    def set_manager(self, user_id: UUID, manager_id: Optional[UUID], *, ctx: AuditContext) -> User:
        user = self.get_required(user_id)
        return self.update_fields(user, {"manager_id": manager_id}, ctx=ctx, description="Set manager")
