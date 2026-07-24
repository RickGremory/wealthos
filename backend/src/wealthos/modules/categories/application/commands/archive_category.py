"""ArchiveCategory command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.exceptions import (
    CategoryHasActiveChildren,
    CategoryNotFoundError,
)
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)


@dataclass(frozen=True, slots=True)
class ArchiveCategoryInput:
    organization_id: UUID
    category_id: UUID


class ArchiveCategoryCommand:
    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    def execute(self, data: ArchiveCategoryInput) -> Category:
        category = self._repository.get_by_id(data.organization_id, data.category_id)
        if category is None:
            raise CategoryNotFoundError("Category not found.")

        active_children = self._repository.count_active_children(
            data.organization_id,
            data.category_id,
        )
        if active_children > 0:
            raise CategoryHasActiveChildren(
                "Archive active child categories before archiving the parent."
            )

        category.archive()
        return self._repository.save(category)
