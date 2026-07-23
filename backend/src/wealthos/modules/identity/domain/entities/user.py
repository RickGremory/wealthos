"""User aggregate — identity root for WealthOS."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from wealthos.modules.identity.domain.value_objects.display_name import DisplayName
from wealthos.modules.identity.domain.value_objects.email import Email


@dataclass(slots=True)
class User:
    """Authenticated person who can belong to one or more organizations."""

    id: UUID
    email: Email
    display_name: DisplayName
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        email: str,
        display_name: str,
        user_id: UUID | None = None,
    ) -> User:
        now = datetime.now(UTC)
        return cls(
            id=user_id or uuid4(),
            email=Email(email),
            display_name=DisplayName(display_name),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
