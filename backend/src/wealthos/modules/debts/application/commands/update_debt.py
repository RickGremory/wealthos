"""UpdateDebt command (immutable account/type/currency)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.exceptions import DebtNotFoundError
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class UpdateDebtInput:
    organization_id: UUID
    debt_id: UUID
    name: str | None = None
    annual_interest_rate: Decimal | None = None
    minimum_payment: Decimal | None = None
    maturity_date: date | None = None
    payment_day: int | None = None
    statement_day: int | None = None
    notes: str | None = None
    fields_set: frozenset[str] = field(default_factory=frozenset)


class UpdateDebtCommand:
    def __init__(self, debts: DebtRepository) -> None:
        self._debts = debts

    def execute(self, data: UpdateDebtInput) -> Debt:
        debt = self._debts.get_by_id(data.organization_id, data.debt_id)
        if debt is None:
            raise DebtNotFoundError("Debt not found.")

        if "name" in data.fields_set and data.name is not None:
            debt.rename(data.name)
        if "annual_interest_rate" in data.fields_set and data.annual_interest_rate is not None:
            debt.change_interest_rate(data.annual_interest_rate)
        if "minimum_payment" in data.fields_set and data.minimum_payment is not None:
            debt.change_minimum_payment(
                Money(data.minimum_payment, debt.minimum_payment.currency)
            )
        if "maturity_date" in data.fields_set:
            debt.change_maturity_date(data.maturity_date)
        if "payment_day" in data.fields_set:
            debt.change_payment_day(data.payment_day)
        if "statement_day" in data.fields_set:
            debt.change_statement_day(data.statement_day)
        if "notes" in data.fields_set:
            debt.change_notes(data.notes)

        return self._debts.save(debt)
