"""Create an account and post an auditable opening-balance adjustment atomically."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.accounts.domain.repositories.account_repository import AccountRepository
from wealthos.modules.transactions.application.commands.create_adjustment import (
    CreateAdjustmentCommand,
    CreateAdjustmentInput,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class CreateAccountWithOpeningBalanceInput:
    organization_id: UUID
    name: str
    account_type: str
    currency: str
    created_by_user_id: UUID
    opening_balance: Decimal = Decimal("0.00")
    opening_balance_date: date | None = None
    institution_name: str | None = None
    last_four: str | None = None


class CreateAccountWithOpeningBalanceCommand:
    """Create Account + optional opening adjustment in one unit of work.

    The account stores ``opening_balance`` as metadata. When the amount is
    non-zero, ``current_balance`` starts at zero and an adjustment transaction
    applies the delta so the ledger stays auditable.
    """

    def __init__(
        self,
        accounts: AccountRepository,
        adjustments: CreateAdjustmentCommand,
    ) -> None:
        self._accounts = accounts
        self._adjustments = adjustments

    def execute(self, data: CreateAccountWithOpeningBalanceInput) -> Account:
        account = Account.create(
            organization_id=data.organization_id,
            name=data.name,
            account_type=data.account_type,
            currency=data.currency,
            opening_balance=data.opening_balance,
            institution_name=data.institution_name,
            last_four=data.last_four,
        )

        if data.opening_balance != Decimal("0.00"):
            account.current_balance = Money(Decimal("0.00"), account.currency)

        account = self._accounts.add(account)

        if data.opening_balance == Decimal("0.00"):
            return account

        occurred_at = _opening_occurred_at(data.opening_balance_date)
        self._adjustments.execute(
            CreateAdjustmentInput(
                organization_id=data.organization_id,
                account_id=account.id,
                amount=data.opening_balance,
                description=f"Saldo inicial · {account.name.value}",
                occurred_at=occurred_at,
                created_by_user_id=data.created_by_user_id,
                notes="opening_balance",
            )
        )

        refreshed = self._accounts.get_by_id(data.organization_id, account.id)
        return refreshed if refreshed is not None else account


def _opening_occurred_at(value: date | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    return datetime.combine(value, time(12, 0), tzinfo=UTC)
