"""Map TaxPayment ↔ TaxPaymentModel."""

from __future__ import annotations

from wealthos.modules.taxes.domain.entities.tax_payment import TaxPayment
from wealthos.modules.taxes.domain.value_objects.tax_type import TaxType
from wealthos.modules.taxes.infrastructure.models.tax_models import TaxPaymentModel
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class TaxPaymentMapper(BaseMapper[TaxPaymentModel, TaxPayment]):
    def to_entity(self, model: TaxPaymentModel) -> TaxPayment:
        return TaxPayment(
            id=model.id,
            organization_id=model.organization_id,
            tax_period_id=model.tax_period_id,
            tax_type=TaxType(model.tax_type),
            transaction_id=model.transaction_id,
            source_account_id=model.source_account_id,
            amount=Money(model.amount, model.currency),
            paid_at=model.paid_at,
            reference=model.reference,
            notes=model.notes,
            idempotency_key=model.idempotency_key,
            created_by_user_id=model.created_by_user_id,
            created_at=model.created_at,
        )

    def to_model(self, entity: TaxPayment) -> TaxPaymentModel:
        return TaxPaymentModel(
            id=entity.id,
            organization_id=entity.organization_id,
            tax_period_id=entity.tax_period_id,
            tax_type=entity.tax_type.value,
            transaction_id=entity.transaction_id,
            source_account_id=entity.source_account_id,
            amount=entity.amount.amount,
            currency=entity.amount.currency.value,
            paid_at=entity.paid_at,
            reference=entity.reference,
            notes=entity.notes,
            idempotency_key=entity.idempotency_key,
            created_by_user_id=entity.created_by_user_id,
            created_at=entity.created_at,
        )
