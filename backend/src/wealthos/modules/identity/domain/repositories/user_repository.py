"""Persistence port for User aggregates."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.identity.domain.entities.user import User
from wealthos.modules.identity.domain.value_objects.email import Email


class UserRepository(Protocol):
    """Domain-facing user repository."""

    def add(self, user: User, *, password_hash: str) -> User:
        """Persist a new user with its password hash and return the aggregate."""
        ...

    def get_by_id(self, user_id: UUID) -> User | None:
        """Fetch by UUID identity."""
        ...

    def get_by_email(self, email: Email) -> User | None:
        """Fetch by normalized email."""
        ...

    def get_password_hash(self, user_id: UUID) -> str | None:
        """Return the stored password hash for credential verification."""
        ...
