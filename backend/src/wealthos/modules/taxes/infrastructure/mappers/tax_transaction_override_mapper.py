"""Map TaxTransactionOverride ↔ TaxTransactionOverrideModel."""

from __future__ import annotations

from decimal import Decimal

from wealthos.modules.taxes.domain.entities.tax_transaction_override import (
    TaxTransactionOverride,
)
from wealthos.modules.taxes.domain.value_objects.percentage import Percentage
from wealthos.modules.taxes.domain.value_objects.tax_treatment import TaxTreatment
from wealthos.modules.taxes.infrastructure.models.tax_models import (
    TaxTransactionOverrideModel,
)
from wealthos.shared.base import BaseMapper


class TaxTransactionOverrideMapper(BaseMapper[TaxTransactionOverrideModel, TaxTransactionOverride]):
    def to_entity(self, model: TaxTransactionOverrideModel) -> TaxTransactionOverride:
        return TaxTransactionOverride(
            id=model.id,
            organization_id=model.organization_id,
            tax_profile_id=model.tax_profile_id,
            transaction_id=model.transaction_id,
            tax_treatment=TaxTreatment(model.tax_treatment),
            deductibility_percentage=Percentage(
                model.deductibility_percentage,
                max_value=Decimal("100"),
            ),
            reason=model.reason,
            created_by_user_id=model.created_by_user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: TaxTransactionOverride) -> TaxTransactionOverrideModel:
        return TaxTransactionOverrideModel(
            id=entity.id,
            organization_id=entity.organization_id,
            tax_profile_id=entity.tax_profile_id,
            transaction_id=entity.transaction_id,
            tax_treatment=entity.tax_treatment.value,
            deductibility_percentage=entity.deductibility_percentage.value,
            reason=entity.reason,
            created_by_user_id=entity.created_by_user_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def apply_to_model(
        self,
        entity: TaxTransactionOverride,
        model: TaxTransactionOverrideModel,
    ) -> TaxTransactionOverrideModel:
        model.tax_treatment = entity.tax_treatment.value
        model.deductibility_percentage = entity.deductibility_percentage.value
        model.reason = entity.reason
        model.updated_at = entity.updated_at
        return model
