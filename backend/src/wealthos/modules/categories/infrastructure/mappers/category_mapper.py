"""Map Category ↔ CategoryModel."""

from __future__ import annotations

from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.value_objects.category_name import CategoryName
from wealthos.modules.categories.domain.value_objects.category_type import CategoryType
from wealthos.modules.categories.infrastructure.models.category_model import CategoryModel
from wealthos.shared.base import BaseMapper


class CategoryMapper(BaseMapper[CategoryModel, Category]):
    def to_entity(self, model: CategoryModel) -> Category:
        return Category(
            id=model.id,
            organization_id=model.organization_id,
            name=CategoryName(model.name),
            category_type=CategoryType(model.category_type),
            parent_id=model.parent_id,
            icon=model.icon,
            color=model.color,
            is_system=model.is_system,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            archived_at=model.archived_at,
        )

    def to_model(self, entity: Category) -> CategoryModel:
        return CategoryModel(
            id=entity.id,
            organization_id=entity.organization_id,
            name=entity.name.value,
            normalized_name=entity.name.normalized,
            category_type=entity.category_type.value,
            parent_id=entity.parent_id,
            icon=entity.icon,
            color=entity.color,
            is_system=entity.is_system,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            archived_at=entity.archived_at,
        )

    def apply_to_model(self, entity: Category, model: CategoryModel) -> CategoryModel:
        model.name = entity.name.value
        model.normalized_name = entity.name.normalized
        model.category_type = entity.category_type.value
        model.parent_id = entity.parent_id
        model.icon = entity.icon
        model.color = entity.color
        model.is_system = entity.is_system
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at
        model.archived_at = entity.archived_at
        return model
