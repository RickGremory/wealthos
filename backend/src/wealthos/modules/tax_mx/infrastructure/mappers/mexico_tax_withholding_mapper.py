"""Map MexicoTaxWithholding ↔ model."""

from __future__ import annotations

from decimal import Decimal

from wealthos.modules.tax_mx.domain.entities.mexico_tax_withholding import MexicoTaxWithholding
from wealthos.modules.tax_mx.domain.value_objects.estimation import MexicoWithholdingType
from wealthos.modules.tax_mx.domain.value_objects.rfc import RFC
from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import MexicoTaxWithholdingModel
from wealthos.modules.taxes.domain.value_objects.percentage import Percentage
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class MexicoTaxWithholdingMapper(BaseMapper[MexicoTaxWithholdingModel, MexicoTaxWithholding]):
    def to_entity(self, model: MexicoTaxWithholdingModel) -> MexicoTaxWithholding:
        currency = model.currency
        return MexicoTaxWithholding(
            id=model.id,
            organization_id=model.organization_id,
            transaction_id=model.transaction_id,
            withholding_type=MexicoWithholdingType(model.withholding_type),
            base_amount=Money(Decimal(str(model.base_amount)), currency),
            rate=Percentage(model.rate) if model.rate is not None else None,
            amount=Money(Decimal(str(model.amount)), currency),
            withheld_by_rfc=RFC(model.withheld_by_rfc) if model.withheld_by_rfc else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: MexicoTaxWithholding) -> MexicoTaxWithholdingModel:
        currency = entity.amount.currency.value
        return MexicoTaxWithholdingModel(
            id=entity.id,
            organization_id=entity.organization_id,
            transaction_id=entity.transaction_id,
            withholding_type=entity.withholding_type.value,
            base_amount=entity.base_amount.amount,
            rate=entity.rate.value if entity.rate else None,
            amount=entity.amount.amount,
            currency=currency,
            withheld_by_rfc=entity.withheld_by_rfc.value if entity.withheld_by_rfc else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
