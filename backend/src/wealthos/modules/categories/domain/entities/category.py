"""Category aggregate — hierarchical financial classification."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from wealthos.modules.categories.domain.exceptions import (
    CategoryAlreadyArchived,
    SystemCategoryCannotBeArchived,
)
from wealthos.modules.categories.domain.value_objects.category_name import CategoryName
from wealthos.modules.categories.domain.value_objects.category_type import CategoryType


@dataclass(slots=True)
class Category:
    """Category belonging to exactly one organization (max depth: 2)."""

    id: UUID
    organization_id: UUID
    name: CategoryName
    category_type: CategoryType
    parent_id: UUID | None
    icon: str | None
    color: str | None
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        name: str,
        category_type: str,
        parent_id: UUID | None = None,
        icon: str | None = None,
        color: str | None = None,
        is_system: bool = False,
        category_id: UUID | None = None,
    ) -> Category:
        now = datetime.now(UTC)
        return cls(
            id=category_id or uuid4(),
            organization_id=organization_id,
            name=CategoryName(name),
            category_type=CategoryType(category_type),
            parent_id=parent_id,
            icon=_clean_optional(icon),
            color=_clean_optional(color),
            is_system=is_system,
            is_active=True,
            created_at=now,
            updated_at=now,
            archived_at=None,
        )

    def rename(self, name: CategoryName | str) -> None:
        self.name = name if isinstance(name, CategoryName) else CategoryName(name)
        self.updated_at = datetime.now(UTC)

    def change_icon(self, icon: str | None) -> None:
        self.icon = _clean_optional(icon)
        self.updated_at = datetime.now(UTC)

    def change_color(self, color: str | None) -> None:
        self.color = _clean_optional(color)
        self.updated_at = datetime.now(UTC)

    def archive(self) -> None:
        if self.is_system:
            raise SystemCategoryCannotBeArchived("System categories cannot be archived.")
        if not self.is_active or self.archived_at is not None:
            raise CategoryAlreadyArchived("Category is already archived.")
        now = datetime.now(UTC)
        self.is_active = False
        self.archived_at = now
        self.updated_at = now


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None
