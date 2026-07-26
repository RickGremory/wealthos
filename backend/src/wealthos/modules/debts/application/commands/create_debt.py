"""CreateDebt command."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.exceptions import (
    DebtAccountInactive,
    DebtAccountMustBeLiability,
    DebtAccountNotFound,
    DebtAlreadyExistsForAccount,
    DebtCurrencyMismatch,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class CreateDebtInput:
    organization_id: UUID
    account_id: UUID
    name: str
    debt_type: str
    creditor: str | None = None
    priority: str = "medium"
    interest_rate: Decimal | None = None
    minimum_payment: Decimal | None = None
    scheduled_payment: Decimal | None = None
    credit_limit: Decimal | None = None
    original_amount: Decimal | None = None
    maturity_date: date | None = None
    due_day: int | None = None
    statement_day: int | None = None
    notes: str | None = None


class CreateDebtCommand:
    def __init__(self, debts: DebtRepository, accounts: AccountRepository) -> None:
        self._debts = debts
        self._accounts = accounts

    def execute(self, data: CreateDebtInput) -> Debt:
        account = self._accounts.get_by_id(data.organization_id, data.account_id)
        if account is None:
            raise DebtAccountNotFound("Linked account not found.")
        if not account.is_active:
            raise DebtAccountInactive("Cannot link an archived account.")
        if not account.account_type.is_liability:
            raise DebtAccountMustBeLiability("Debt must be linked to a liability account.")
        existing = self._debts.get_active_by_account(
            data.organization_id,
            data.account_id,
        )
        if existing is not None:
            raise DebtAlreadyExistsForAccount(
                "A commitment already exists for this account."
            )

        currency = account.currency.value

        def _money(amount: Decimal | None) -> Money | None:
            if amount is None:
                return None
            return Money(amount, currency)

        debt = Debt.create(
            organization_id=data.organization_id,
            account_id=data.account_id,
            name=data.name,
            debt_type=data.debt_type,
            currency=currency,
            creditor=data.creditor,
            priority=data.priority,
            interest_rate=data.interest_rate,
            minimum_payment=_money(data.minimum_payment),
            scheduled_payment=_money(data.scheduled_payment),
            credit_limit=_money(data.credit_limit),
            original_amount=_money(data.original_amount),
            maturity_date=data.maturity_date,
            due_day=data.due_day,
            statement_day=data.statement_day,
            notes=data.notes,
        )
        if debt.currency != currency:
            raise DebtCurrencyMismatch("Debt currency must match the account currency.")
        return self._debts.add(debt)
