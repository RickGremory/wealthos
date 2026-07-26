"""UpdateDebt command (immutable account/type/currency)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.exceptions import (
    DebtConcurrentUpdate,
    DebtNotFoundError,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class UpdateDebtInput:
    organization_id: UUID
    debt_id: UUID
    name: str | None = None
    creditor: str | None = None
    priority: str | None = None
    interest_rate: Decimal | None = None
    minimum_payment: Decimal | None = None
    scheduled_payment: Decimal | None = None
    credit_limit: Decimal | None = None
    maturity_date: date | None = None
    due_day: int | None = None
    statement_day: int | None = None
    notes: str | None = None
    expected_version: int | None = None
    fields_set: frozenset[str] = field(default_factory=frozenset)


class UpdateDebtCommand:
    def __init__(self, debts: DebtRepository) -> None:
        self._debts = debts

    def execute(self, data: UpdateDebtInput) -> Debt:
        debt = self._debts.get_by_id(data.organization_id, data.debt_id)
        if debt is None:
            raise DebtNotFoundError("Debt not found.")

        if data.expected_version is not None and data.expected_version != debt.version:
            raise DebtConcurrentUpdate(
                "The commitment was modified by another request. Refresh and try again."
            )

        if "name" in data.fields_set and data.name is not None:
            debt.rename(data.name)
        if "creditor" in data.fields_set:
            debt.change_creditor(data.creditor)
        if "priority" in data.fields_set and data.priority is not None:
            debt.change_priority(data.priority)
        if "interest_rate" in data.fields_set:
            debt.change_interest_rate(data.interest_rate)
        if "minimum_payment" in data.fields_set:
            money = (
                Money(data.minimum_payment, debt.currency)
                if data.minimum_payment is not None
                else None
            )
            debt.change_minimum_payment(money)
        if "scheduled_payment" in data.fields_set:
            money = (
                Money(data.scheduled_payment, debt.currency)
                if data.scheduled_payment is not None
                else None
            )
            debt.change_scheduled_payment(money)
        if "credit_limit" in data.fields_set:
            money = (
                Money(data.credit_limit, debt.currency)
                if data.credit_limit is not None
                else None
            )
            debt.change_credit_limit(money)
        if "maturity_date" in data.fields_set:
            debt.change_maturity_date(data.maturity_date)
        if "due_day" in data.fields_set:
            debt.change_due_day(data.due_day)
        if "statement_day" in data.fields_set:
            debt.change_statement_day(data.statement_day)
        if "notes" in data.fields_set:
            debt.change_notes(data.notes)

        debt.bump_version()
        return self._debts.save(debt)
