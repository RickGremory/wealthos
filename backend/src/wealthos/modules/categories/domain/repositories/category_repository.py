"""Persistence port for Category aggregates."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.value_objects.category_type import CategoryType


class CategoryRepository(Protocol):
    """Domain-facing category repository (always scoped by organization)."""

    def add(self, category: Category) -> Category: ...

    def add_many(self, categories: list[Category]) -> list[Category]: ...

    def get_by_id(self, organization_id: UUID, category_id: UUID) -> Category | None: ...

    def exists_by_normalized_name(
        self,
        organization_id: UUID,
        category_type: CategoryType,
        normalized_name: str,
        parent_id: UUID | None,
        *,
        exclude_id: UUID | None = None,
    ) -> bool: ...

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        category_type: CategoryType | None = None,
        include_archived: bool = False,
    ) -> list[Category]: ...

    def count_active_children(
        self,
        organization_id: UUID,
        category_id: UUID,
    ) -> int: ...

    def save(self, category: Category) -> Category: ...
