"""SQLAlchemy MexicoTaxCategoryMappingRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.tax_mx.domain.entities.mexico_tax_classification import (
    MexicoTaxCategoryMapping,
)
from wealthos.modules.tax_mx.infrastructure.mappers.mexico_tax_category_mapping_mapper import (
    MexicoTaxCategoryMappingMapper,
)
from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import (
    MexicoTaxCategoryMappingModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyMexicoTaxCategoryMappingRepository(BaseRepository[MexicoTaxCategoryMappingModel]):
    def __init__(
        self, session: Session, mapper: MexicoTaxCategoryMappingMapper | None = None
    ) -> None:
        super().__init__(session, MexicoTaxCategoryMappingModel)
        self._mapper = mapper or MexicoTaxCategoryMappingMapper()

    def add(self, mapping: MexicoTaxCategoryMapping) -> MexicoTaxCategoryMapping:
        model = self._mapper.to_model(mapping)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(self, organization_id: UUID, mapping_id: UUID) -> MexicoTaxCategoryMapping | None:
        stmt = select(MexicoTaxCategoryMappingModel).where(
            MexicoTaxCategoryMappingModel.organization_id == organization_id,
            MexicoTaxCategoryMappingModel.id == mapping_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_by_profile(
        self, organization_id: UUID, tax_profile_id: UUID
    ) -> list[MexicoTaxCategoryMapping]:
        stmt = select(MexicoTaxCategoryMappingModel).where(
            MexicoTaxCategoryMappingModel.organization_id == organization_id,
            MexicoTaxCategoryMappingModel.tax_profile_id == tax_profile_id,
        )
        return [self._mapper.to_entity(m) for m in self.session.scalars(stmt)]

    def get_by_category(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        category_id: UUID,
    ) -> MexicoTaxCategoryMapping | None:
        stmt = select(MexicoTaxCategoryMappingModel).where(
            MexicoTaxCategoryMappingModel.organization_id == organization_id,
            MexicoTaxCategoryMappingModel.tax_profile_id == tax_profile_id,
            MexicoTaxCategoryMappingModel.category_id == category_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def upsert(self, mapping: MexicoTaxCategoryMapping) -> MexicoTaxCategoryMapping:
        existing = self.get_by_category(
            mapping.organization_id,
            mapping.tax_profile_id,
            mapping.category_id,
        )
        if existing is None:
            return self.add(mapping)

        existing.update(
            vat_treatment=mapping.vat_treatment.value,
            income_treatment=(mapping.income_treatment.value if mapping.income_treatment else None),
            expense_treatment=(
                mapping.expense_treatment.value if mapping.expense_treatment else None
            ),
            deductibility_percentage=mapping.deductibility_percentage.value,
            vat_creditable_percentage=mapping.vat_creditable_percentage.value,
            requires_cfdi=mapping.requires_cfdi,
            requires_payment_evidence=mapping.requires_payment_evidence,
            clear_income_treatment=mapping.income_treatment is None,
            clear_expense_treatment=mapping.expense_treatment is None,
            fields_set=frozenset(
                {
                    "vat_treatment",
                    "income_treatment",
                    "expense_treatment",
                    "deductibility_percentage",
                    "vat_creditable_percentage",
                    "requires_cfdi",
                    "requires_payment_evidence",
                }
            ),
        )
        return self.save(existing)

    def save(self, mapping: MexicoTaxCategoryMapping) -> MexicoTaxCategoryMapping:
        model = self.session.get(MexicoTaxCategoryMappingModel, mapping.id)
        if model is None or model.organization_id != mapping.organization_id:
            raise LookupError("Mapping not found.")
        self._mapper.apply_to_model(mapping, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)
