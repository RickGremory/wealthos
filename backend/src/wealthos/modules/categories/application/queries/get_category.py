"""GetCategory query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.exceptions import CategoryNotFoundError
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)


class GetCategoryQuery:
    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    def execute(self, organization_id: UUID, category_id: UUID) -> Category:
        category = self._repository.get_by_id(organization_id, category_id)
        if category is None:
            raise CategoryNotFoundError("Category not found.")
        return category
