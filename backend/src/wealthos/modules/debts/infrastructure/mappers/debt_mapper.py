"""Map Debt ↔ DebtModel."""

from __future__ import annotations

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.value_objects.debt_name import DebtName
from wealthos.modules.debts.domain.value_objects.debt_priority import DebtPriority
from wealthos.modules.debts.domain.value_objects.debt_status import DebtStatus
from wealthos.modules.debts.domain.value_objects.debt_type import DebtType
from wealthos.modules.debts.domain.value_objects.interest_rate import InterestRate
from wealthos.modules.debts.infrastructure.models.debt_model import DebtModel
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


def _money(amount, currency: str) -> Money | None:
    if amount is None:
        return None
    return Money(amount, currency)


class DebtMapper(BaseMapper[DebtModel, Debt]):
    def to_entity(self, model: DebtModel) -> Debt:
        currency = model.currency
        return Debt(
            id=model.id,
            organization_id=model.organization_id,
            account_id=model.account_id,
            name=DebtName(model.name),
            debt_type=DebtType(model.debt_type),
            creditor=model.creditor,
            currency=currency,
            priority=DebtPriority(model.priority),
            interest_rate=(
                InterestRate(model.interest_rate)
                if model.interest_rate is not None
                else None
            ),
            minimum_payment=_money(model.minimum_payment, currency),
            scheduled_payment=_money(model.scheduled_payment, currency),
            credit_limit=_money(model.credit_limit, currency),
            original_amount=_money(model.original_amount, currency),
            statement_day=model.statement_day,
            due_day=model.due_day,
            maturity_date=model.maturity_date,
            status=DebtStatus(model.status),
            notes=model.notes,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
            closed_at=model.closed_at,
            archived_at=model.archived_at,
        )

    def to_model(self, entity: Debt) -> DebtModel:
        return DebtModel(
            id=entity.id,
            organization_id=entity.organization_id,
            account_id=entity.account_id,
            name=entity.name.value,
            debt_type=entity.debt_type.value,
            creditor=entity.creditor,
            currency=entity.currency,
            status=entity.status.value,
            priority=entity.priority.value,
            interest_rate=(
                entity.interest_rate.annual_percentage if entity.interest_rate else None
            ),
            minimum_payment=(
                entity.minimum_payment.amount if entity.minimum_payment else None
            ),
            scheduled_payment=(
                entity.scheduled_payment.amount if entity.scheduled_payment else None
            ),
            credit_limit=entity.credit_limit.amount if entity.credit_limit else None,
            original_amount=(
                entity.original_amount.amount if entity.original_amount else None
            ),
            statement_day=entity.statement_day,
            due_day=entity.due_day,
            maturity_date=entity.maturity_date,
            notes=entity.notes,
            version=entity.version,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            closed_at=entity.closed_at,
            archived_at=entity.archived_at,
        )

    def apply_to_model(self, entity: Debt, model: DebtModel) -> DebtModel:
        model.name = entity.name.value
        model.creditor = entity.creditor
        model.priority = entity.priority.value
        model.interest_rate = (
            entity.interest_rate.annual_percentage if entity.interest_rate else None
        )
        model.minimum_payment = (
            entity.minimum_payment.amount if entity.minimum_payment else None
        )
        model.scheduled_payment = (
            entity.scheduled_payment.amount if entity.scheduled_payment else None
        )
        model.credit_limit = (
            entity.credit_limit.amount if entity.credit_limit else None
        )
        model.original_amount = (
            entity.original_amount.amount if entity.original_amount else None
        )
        model.maturity_date = entity.maturity_date
        model.due_day = entity.due_day
        model.statement_day = entity.statement_day
        model.status = entity.status.value
        model.notes = entity.notes
        model.version = entity.version
        model.updated_at = entity.updated_at
        model.closed_at = entity.closed_at
        model.archived_at = entity.archived_at
        return model
