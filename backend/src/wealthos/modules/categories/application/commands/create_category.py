"""CreateCategory command with hierarchy validation."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.exceptions import (
    CategoryDepthExceeded,
    CategoryTypeMismatch,
    DuplicateCategory,
    ParentCategoryInactive,
    ParentCategoryNotFound,
)
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.categories.domain.value_objects.category_name import CategoryName
from wealthos.modules.categories.domain.value_objects.category_type import CategoryType


@dataclass(frozen=True, slots=True)
class CreateCategoryInput:
    organization_id: UUID
    name: str
    category_type: str
    parent_id: UUID | None = None
    icon: str | None = None
    color: str | None = None


class CreateCategoryCommand:
    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    def execute(self, data: CreateCategoryInput) -> Category:
        name = CategoryName(data.name)
        category_type = CategoryType(data.category_type)

        if data.parent_id is not None:
            parent = self._repository.get_by_id(data.organization_id, data.parent_id)
            if parent is None:
                raise ParentCategoryNotFound("Parent category was not found.")
            if not parent.is_active:
                raise ParentCategoryInactive("Parent category is inactive.")
            if parent.parent_id is not None:
                raise CategoryDepthExceeded(
                    "Categories support only two levels (root → subcategory)."
                )
            if parent.category_type != category_type:
                raise CategoryTypeMismatch("Subcategory type must match the parent category type.")

        if self._repository.exists_by_normalized_name(
            data.organization_id,
            category_type,
            name.normalized,
            data.parent_id,
        ):
            raise DuplicateCategory("A category with this name already exists at this level.")

        category = Category.create(
            organization_id=data.organization_id,
            name=data.name,
            category_type=data.category_type,
            parent_id=data.parent_id,
            icon=data.icon,
            color=data.color,
        )
        return self._repository.add(category)
