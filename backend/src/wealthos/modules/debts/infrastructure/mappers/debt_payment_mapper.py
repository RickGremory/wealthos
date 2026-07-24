"""Map DebtPayment ↔ DebtPaymentModel."""

from __future__ import annotations

from wealthos.modules.debts.domain.entities.debt_payment import DebtPayment
from wealthos.modules.debts.infrastructure.models.debt_model import DebtPaymentModel
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class DebtPaymentMapper(BaseMapper[DebtPaymentModel, DebtPayment]):
    def to_entity(self, model: DebtPaymentModel) -> DebtPayment:
        currency = model.currency
        principal = None
        interest = None
        if model.principal_amount is not None:
            principal = Money(model.principal_amount, currency)
        if model.interest_amount is not None:
            interest = Money(model.interest_amount, currency)
        return DebtPayment(
            id=model.id,
            organization_id=model.organization_id,
            debt_id=model.debt_id,
            transaction_id=model.transaction_id,
            amount=Money(model.amount, currency),
            principal_amount=principal,
            interest_amount=interest,
            paid_at=model.paid_at,
            created_by_user_id=model.created_by_user_id,
            created_at=model.created_at,
        )

    def to_model(self, entity: DebtPayment) -> DebtPaymentModel:
        currency = entity.amount.currency.value
        return DebtPaymentModel(
            id=entity.id,
            organization_id=entity.organization_id,
            debt_id=entity.debt_id,
            transaction_id=entity.transaction_id,
            amount=entity.amount.amount,
            currency=currency,
            principal_amount=(entity.principal_amount.amount if entity.principal_amount else None),
            interest_amount=(entity.interest_amount.amount if entity.interest_amount else None),
            paid_at=entity.paid_at,
            created_by_user_id=entity.created_by_user_id,
            created_at=entity.created_at,
        )
