"""SQLAlchemy implementation of CategoryRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.value_objects.category_type import CategoryType
from wealthos.modules.categories.infrastructure.mappers.category_mapper import (
    CategoryMapper,
)
from wealthos.modules.categories.infrastructure.models.category_model import CategoryModel
from wealthos.shared.base import BaseRepository


class SqlAlchemyCategoryRepository(BaseRepository[CategoryModel]):
    def __init__(self, session: Session, mapper: CategoryMapper | None = None) -> None:
        super().__init__(session, CategoryModel)
        self._mapper = mapper or CategoryMapper()

    def add(self, category: Category) -> Category:
        model = self._mapper.to_model(category)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def add_many(self, categories: list[Category]) -> list[Category]:
        models = [self._mapper.to_model(category) for category in categories]
        for model in models:
            super().add(model)
        self.flush()
        for model in models:
            self.refresh(model)
        return [self._mapper.to_entity(model) for model in models]

    def get_by_id(self, organization_id: UUID, category_id: UUID) -> Category | None:
        stmt = select(CategoryModel).where(
            CategoryModel.organization_id == organization_id,
            CategoryModel.id == category_id,
        )
        model = self.session.scalars(stmt).first()
        if model is None:
            return None
        return self._mapper.to_entity(model)

    def exists_by_normalized_name(
        self,
        organization_id: UUID,
        category_type: CategoryType,
        normalized_name: str,
        parent_id: UUID | None,
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        stmt = select(CategoryModel.id).where(
            CategoryModel.organization_id == organization_id,
            CategoryModel.category_type == category_type.value,
            CategoryModel.normalized_name == normalized_name,
        )
        if parent_id is None:
            stmt = stmt.where(CategoryModel.parent_id.is_(None))
        else:
            stmt = stmt.where(CategoryModel.parent_id == parent_id)
        if exclude_id is not None:
            stmt = stmt.where(CategoryModel.id != exclude_id)
        return self.session.scalars(stmt).first() is not None

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        category_type: CategoryType | None = None,
        include_archived: bool = False,
    ) -> list[Category]:
        stmt = select(CategoryModel).where(
            CategoryModel.organization_id == organization_id,
        )
        if category_type is not None:
            stmt = stmt.where(CategoryModel.category_type == category_type.value)
        if not include_archived:
            stmt = stmt.where(CategoryModel.is_active.is_(True))
        stmt = stmt.order_by(
            CategoryModel.category_type.asc(),
            CategoryModel.parent_id.asc().nullsfirst(),
            CategoryModel.name.asc(),
        )
        models = self.session.scalars(stmt).all()
        return [self._mapper.to_entity(model) for model in models]

    def count_active_children(
        self,
        organization_id: UUID,
        category_id: UUID,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(CategoryModel)
            .where(
                CategoryModel.organization_id == organization_id,
                CategoryModel.parent_id == category_id,
                CategoryModel.is_active.is_(True),
            )
        )
        return int(self.session.scalar(stmt) or 0)

    def save(self, category: Category) -> Category:
        model = self.session.get(CategoryModel, category.id)
        if model is None or model.organization_id != category.organization_id:
            raise LookupError("Category not found for save.")
        self._mapper.apply_to_model(category, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)
