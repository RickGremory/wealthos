"""Map Debt ↔ DebtModel."""

from __future__ import annotations

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.value_objects.debt_name import DebtName
from wealthos.modules.debts.domain.value_objects.debt_status import DebtStatus
from wealthos.modules.debts.domain.value_objects.debt_type import DebtType
from wealthos.modules.debts.domain.value_objects.interest_rate import InterestRate
from wealthos.modules.debts.infrastructure.models.debt_model import DebtModel
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class DebtMapper(BaseMapper[DebtModel, Debt]):
    def to_entity(self, model: DebtModel) -> Debt:
        currency = model.currency
        original = None
        if model.original_principal is not None:
            original = Money(model.original_principal, currency)
        return Debt(
            id=model.id,
            organization_id=model.organization_id,
            account_id=model.account_id,
            name=DebtName(model.name),
            debt_type=DebtType(model.debt_type),
            annual_interest_rate=InterestRate(model.annual_interest_rate),
            minimum_payment=Money(model.minimum_payment, currency),
            original_principal=original,
            opened_at=model.opened_at,
            maturity_date=model.maturity_date,
            payment_day=model.payment_day,
            statement_day=model.statement_day,
            status=DebtStatus(model.status),
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            paid_off_at=model.paid_off_at,
            archived_at=model.archived_at,
        )

    def to_model(self, entity: Debt) -> DebtModel:
        currency = entity.minimum_payment.currency.value
        return DebtModel(
            id=entity.id,
            organization_id=entity.organization_id,
            account_id=entity.account_id,
            name=entity.name.value,
            debt_type=entity.debt_type.value,
            currency=currency,
            annual_interest_rate=entity.annual_interest_rate.annual_percentage,
            minimum_payment=entity.minimum_payment.amount,
            original_principal=(
                entity.original_principal.amount if entity.original_principal else None
            ),
            opened_at=entity.opened_at,
            maturity_date=entity.maturity_date,
            payment_day=entity.payment_day,
            statement_day=entity.statement_day,
            status=entity.status.value,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            paid_off_at=entity.paid_off_at,
            archived_at=entity.archived_at,
        )

    def apply_to_model(self, entity: Debt, model: DebtModel) -> DebtModel:
        model.name = entity.name.value
        model.annual_interest_rate = entity.annual_interest_rate.annual_percentage
        model.minimum_payment = entity.minimum_payment.amount
        model.maturity_date = entity.maturity_date
        model.payment_day = entity.payment_day
        model.statement_day = entity.statement_day
        model.status = entity.status.value
        model.notes = entity.notes
        model.updated_at = entity.updated_at
        model.paid_off_at = entity.paid_off_at
        model.archived_at = entity.archived_at
        return model
