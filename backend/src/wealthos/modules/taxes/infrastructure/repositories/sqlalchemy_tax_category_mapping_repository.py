"""SQLAlchemy TaxCategoryMappingRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.taxes.domain.entities.tax_category_mapping import TaxCategoryMapping
from wealthos.modules.taxes.infrastructure.mappers.tax_category_mapping_mapper import (
    TaxCategoryMappingMapper,
)
from wealthos.modules.taxes.infrastructure.models.tax_models import TaxCategoryMappingModel
from wealthos.shared.base import BaseRepository


class SqlAlchemyTaxCategoryMappingRepository(BaseRepository[TaxCategoryMappingModel]):
    def __init__(
        self,
        session: Session,
        mapper: TaxCategoryMappingMapper | None = None,
    ) -> None:
        super().__init__(session, TaxCategoryMappingModel)
        self._mapper = mapper or TaxCategoryMappingMapper()

    def upsert(self, mapping: TaxCategoryMapping) -> TaxCategoryMapping:
        existing = self.get_by_category(
            mapping.organization_id,
            mapping.tax_profile_id,
            mapping.category_id,
        )
        if existing is None:
            model = self._mapper.to_model(mapping)
            super().add(model)
            self.flush()
            self.refresh(model)
            return self._mapper.to_entity(model)

        model = self.session.get(TaxCategoryMappingModel, existing.id)
        assert model is not None
        existing.update(
            tax_treatment=mapping.tax_treatment.value,
            deductibility_percentage=mapping.deductibility_percentage.value,
        )
        self._mapper.apply_to_model(existing, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def list_by_profile(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
    ) -> list[TaxCategoryMapping]:
        stmt = select(TaxCategoryMappingModel).where(
            TaxCategoryMappingModel.organization_id == organization_id,
            TaxCategoryMappingModel.tax_profile_id == tax_profile_id,
        )
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def get_by_category(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        category_id: UUID,
    ) -> TaxCategoryMapping | None:
        stmt = select(TaxCategoryMappingModel).where(
            TaxCategoryMappingModel.organization_id == organization_id,
            TaxCategoryMappingModel.tax_profile_id == tax_profile_id,
            TaxCategoryMappingModel.category_id == category_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None
