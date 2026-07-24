"""Map TaxCategoryMapping ↔ TaxCategoryMappingModel."""

from __future__ import annotations

from decimal import Decimal

from wealthos.modules.taxes.domain.entities.tax_category_mapping import TaxCategoryMapping
from wealthos.modules.taxes.domain.value_objects.percentage import Percentage
from wealthos.modules.taxes.domain.value_objects.tax_treatment import TaxTreatment
from wealthos.modules.taxes.infrastructure.models.tax_models import TaxCategoryMappingModel
from wealthos.shared.base import BaseMapper


class TaxCategoryMappingMapper(BaseMapper[TaxCategoryMappingModel, TaxCategoryMapping]):
    def to_entity(self, model: TaxCategoryMappingModel) -> TaxCategoryMapping:
        return TaxCategoryMapping(
            id=model.id,
            organization_id=model.organization_id,
            tax_profile_id=model.tax_profile_id,
            category_id=model.category_id,
            tax_treatment=TaxTreatment(model.tax_treatment),
            deductibility_percentage=Percentage(
                model.deductibility_percentage,
                max_value=Decimal("100"),
            ),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: TaxCategoryMapping) -> TaxCategoryMappingModel:
        return TaxCategoryMappingModel(
            id=entity.id,
            organization_id=entity.organization_id,
            tax_profile_id=entity.tax_profile_id,
            category_id=entity.category_id,
            tax_treatment=entity.tax_treatment.value,
            deductibility_percentage=entity.deductibility_percentage.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def apply_to_model(
        self,
        entity: TaxCategoryMapping,
        model: TaxCategoryMappingModel,
    ) -> TaxCategoryMappingModel:
        model.tax_treatment = entity.tax_treatment.value
        model.deductibility_percentage = entity.deductibility_percentage.value
        model.updated_at = entity.updated_at
        return model
