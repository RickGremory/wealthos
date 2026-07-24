"""Category response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from wealthos.modules.categories.application.queries.list_categories import (
    CategoryTreeNode,
)
from wealthos.modules.categories.domain.entities.category import Category


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    category_type: str
    parent_id: UUID | None
    icon: str | None
    color: str | None
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None

    @classmethod
    def from_entity(cls, category: Category) -> CategoryResponse:
        return cls(
            id=category.id,
            organization_id=category.organization_id,
            name=category.name.value,
            category_type=category.category_type.value,
            parent_id=category.parent_id,
            icon=category.icon,
            color=category.color,
            is_system=category.is_system,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
            archived_at=category.archived_at,
        )


class CategoryTreeItem(CategoryResponse):
    children: list[CategoryTreeItem] = Field(default_factory=list)

    @classmethod
    def from_node(cls, node: CategoryTreeNode) -> CategoryTreeItem:
        base = CategoryResponse.from_entity(node.category)
        return cls(
            **base.model_dump(),
            children=[cls.from_node(child) for child in node.children],
        )
