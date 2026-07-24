"""Map MexicoTaxCategoryMapping."""

from __future__ import annotations

from wealthos.modules.tax_mx.domain.entities.mexico_tax_classification import (
    MexicoTaxCategoryMapping,
)
from wealthos.modules.tax_mx.domain.value_objects.mexico_expense_treatment import (
    MexicoExpenseTreatment,
)
from wealthos.modules.tax_mx.domain.value_objects.mexico_income_treatment import (
    MexicoIncomeTreatment,
)
from wealthos.modules.tax_mx.domain.value_objects.mexico_vat_treatment import (
    MexicoVATTreatment,
)
from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import (
    MexicoTaxCategoryMappingModel,
)
from wealthos.modules.taxes.domain.value_objects.percentage import Percentage
from wealthos.shared.base import BaseMapper


class MexicoTaxCategoryMappingMapper(
    BaseMapper[MexicoTaxCategoryMappingModel, MexicoTaxCategoryMapping]
):
    def to_entity(self, model: MexicoTaxCategoryMappingModel) -> MexicoTaxCategoryMapping:
        return MexicoTaxCategoryMapping(
            id=model.id,
            organization_id=model.organization_id,
            tax_profile_id=model.tax_profile_id,
            category_id=model.category_id,
            income_treatment=(
                MexicoIncomeTreatment(model.income_treatment) if model.income_treatment else None
            ),
            expense_treatment=(
                MexicoExpenseTreatment(model.expense_treatment) if model.expense_treatment else None
            ),
            vat_treatment=MexicoVATTreatment(model.vat_treatment),
            deductibility_percentage=Percentage(model.deductibility_percentage),
            vat_creditable_percentage=Percentage(model.vat_creditable_percentage),
            requires_cfdi=model.requires_cfdi,
            requires_payment_evidence=model.requires_payment_evidence,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: MexicoTaxCategoryMapping) -> MexicoTaxCategoryMappingModel:
        return MexicoTaxCategoryMappingModel(
            id=entity.id,
            organization_id=entity.organization_id,
            tax_profile_id=entity.tax_profile_id,
            category_id=entity.category_id,
            income_treatment=(entity.income_treatment.value if entity.income_treatment else None),
            expense_treatment=(
                entity.expense_treatment.value if entity.expense_treatment else None
            ),
            vat_treatment=entity.vat_treatment.value,
            deductibility_percentage=entity.deductibility_percentage.value,
            vat_creditable_percentage=entity.vat_creditable_percentage.value,
            requires_cfdi=entity.requires_cfdi,
            requires_payment_evidence=entity.requires_payment_evidence,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def apply_to_model(
        self, entity: MexicoTaxCategoryMapping, model: MexicoTaxCategoryMappingModel
    ) -> MexicoTaxCategoryMappingModel:
        model.income_treatment = entity.income_treatment.value if entity.income_treatment else None
        model.expense_treatment = (
            entity.expense_treatment.value if entity.expense_treatment else None
        )
        model.vat_treatment = entity.vat_treatment.value
        model.deductibility_percentage = entity.deductibility_percentage.value
        model.vat_creditable_percentage = entity.vat_creditable_percentage.value
        model.requires_cfdi = entity.requires_cfdi
        model.requires_payment_evidence = entity.requires_payment_evidence
        model.updated_at = entity.updated_at
        return model
