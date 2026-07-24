"""UpdateCategory command."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.exceptions import (
    CategoryNotFoundError,
    DuplicateCategory,
)
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)


@dataclass(frozen=True, slots=True)
class UpdateCategoryInput:
    organization_id: UUID
    category_id: UUID
    name: str | None = None
    icon: str | None = None
    color: str | None = None
    fields_set: frozenset[str] = field(default_factory=frozenset)


class UpdateCategoryCommand:
    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    def execute(self, data: UpdateCategoryInput) -> Category:
        category = self._repository.get_by_id(data.organization_id, data.category_id)
        if category is None:
            raise CategoryNotFoundError("Category not found.")

        if "name" in data.fields_set and data.name is not None:
            category.rename(data.name)
            if self._repository.exists_by_normalized_name(
                data.organization_id,
                category.category_type,
                category.name.normalized,
                category.parent_id,
                exclude_id=category.id,
            ):
                raise DuplicateCategory("A category with this name already exists at this level.")

        if "icon" in data.fields_set:
            category.change_icon(data.icon)
        if "color" in data.fields_set:
            category.change_color(data.color)

        return self._repository.save(category)
