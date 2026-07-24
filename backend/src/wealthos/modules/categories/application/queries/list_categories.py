"""ListCategories query with optional tree shaping."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.categories.domain.value_objects.category_type import CategoryType


@dataclass(frozen=True, slots=True)
class CategoryTreeNode:
    category: Category
    children: list[CategoryTreeNode]


class ListCategoriesQuery:
    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    def execute(
        self,
        organization_id: UUID,
        *,
        category_type: str | None = None,
        include_archived: bool = False,
        as_tree: bool = False,
    ) -> list[Category] | list[CategoryTreeNode]:
        typed = CategoryType(category_type) if category_type else None
        categories = self._repository.list_by_organization(
            organization_id,
            category_type=typed,
            include_archived=include_archived,
        )
        if not as_tree:
            return categories
        return self._build_tree(categories)

    def _build_tree(self, categories: list[Category]) -> list[CategoryTreeNode]:
        children_by_parent: dict[UUID, list[Category]] = {}
        roots: list[Category] = []
        for category in categories:
            if category.parent_id is None:
                roots.append(category)
            else:
                children_by_parent.setdefault(category.parent_id, []).append(category)

        return [
            CategoryTreeNode(
                category=root,
                children=[
                    CategoryTreeNode(category=child, children=[])
                    for child in children_by_parent.get(root.id, [])
                ],
            )
            for root in roots
        ]
