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
    annual_interest_rate: Decimal
    minimum_payment: Decimal
    original_principal: Decimal | None = None
    opened_at: date | None = None
    maturity_date: date | None = None
    payment_day: int | None = None
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
            raise DebtAccountMustBeLiability(
                "Debt must be linked to a liability account."
            )
        existing = self._debts.get_active_by_account(
            data.organization_id,
            data.account_id,
        )
        if existing is not None:
            raise DebtAlreadyExistsForAccount(
                "An active debt already exists for this account."
            )

        currency = account.currency.value
        original = None
        if data.original_principal is not None:
            original = Money(data.original_principal, currency)

        debt = Debt.create(
            organization_id=data.organization_id,
            account_id=data.account_id,
            name=data.name,
            debt_type=data.debt_type,
            annual_interest_rate=data.annual_interest_rate,
            minimum_payment=Money(data.minimum_payment, currency),
            original_principal=original,
            opened_at=data.opened_at,
            maturity_date=data.maturity_date,
            payment_day=data.payment_day,
            statement_day=data.statement_day,
            notes=data.notes,
        )
        if debt.minimum_payment.currency.value != currency:
            raise DebtCurrencyMismatch("Debt currency must match the account currency.")
        return self._debts.add(debt)
