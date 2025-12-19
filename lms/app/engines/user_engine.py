"""User engine.

Keeps controllers thin and centralizes domain decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.user import User
from ..repositories import AuditContext, AuditRepository, UserRepository


@dataclass(frozen=True)
class UserCreated:
    user: User


class UserEngine:
    def __init__(self, session: Session, *, user_repo: UserRepository):
        self.session = session
        self.user_repo = user_repo

    def create_user(self, *, user: User, ctx: AuditContext) -> UserCreated:
        created = self.user_repo.create_user(user, ctx=ctx)
        return UserCreated(user=created)

    def get_user(self, *, user_id: UUID) -> User:
        return self.user_repo.get_required(user_id)
