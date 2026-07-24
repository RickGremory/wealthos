"""Map MexicoTransactionTaxDetails ↔ model."""

from __future__ import annotations

from decimal import Decimal

from wealthos.modules.tax_mx.domain.entities.tax_evidence import MexicoTransactionTaxDetails
from wealthos.modules.tax_mx.domain.value_objects.estimation import TaxDetailCalculationSource
from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import (
    MexicoTransactionTaxDetailsModel,
)
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class MexicoTransactionTaxDetailsMapper(
    BaseMapper[MexicoTransactionTaxDetailsModel, MexicoTransactionTaxDetails]
):
    def to_entity(self, model: MexicoTransactionTaxDetailsModel) -> MexicoTransactionTaxDetails:
        currency = model.currency
        return MexicoTransactionTaxDetails(
            id=model.id,
            organization_id=model.organization_id,
            transaction_id=model.transaction_id,
            subtotal=Money(Decimal(str(model.subtotal)), currency),
            vat_amount=Money(Decimal(str(model.vat_amount)), currency),
            withheld_income_tax=Money(Decimal(str(model.withheld_income_tax)), currency),
            withheld_vat=Money(Decimal(str(model.withheld_vat)), currency),
            other_taxes=Money(Decimal(str(model.other_taxes)), currency),
            total=Money(Decimal(str(model.total)), currency),
            calculation_source=TaxDetailCalculationSource(model.calculation_source),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: MexicoTransactionTaxDetails) -> MexicoTransactionTaxDetailsModel:
        currency = entity.total.currency.value
        return MexicoTransactionTaxDetailsModel(
            id=entity.id,
            organization_id=entity.organization_id,
            transaction_id=entity.transaction_id,
            subtotal=entity.subtotal.amount,
            vat_amount=entity.vat_amount.amount,
            withheld_income_tax=entity.withheld_income_tax.amount,
            withheld_vat=entity.withheld_vat.amount,
            other_taxes=entity.other_taxes.amount,
            total=entity.total.amount,
            currency=currency,
            calculation_source=entity.calculation_source.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def apply_to_model(
        self,
        entity: MexicoTransactionTaxDetails,
        model: MexicoTransactionTaxDetailsModel,
    ) -> MexicoTransactionTaxDetailsModel:
        model.subtotal = entity.subtotal.amount
        model.vat_amount = entity.vat_amount.amount
        model.withheld_income_tax = entity.withheld_income_tax.amount
        model.withheld_vat = entity.withheld_vat.amount
        model.other_taxes = entity.other_taxes.amount
        model.total = entity.total.amount
        model.currency = entity.total.currency.value
        model.calculation_source = entity.calculation_source.value
        model.updated_at = entity.updated_at
        return model
