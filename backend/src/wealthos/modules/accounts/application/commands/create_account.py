"""CreateAccount command."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.accounts.domain.repositories.account_repository import AccountRepository


@dataclass(frozen=True, slots=True)
class CreateAccountInput:
    organization_id: UUID
    name: str
    account_type: str
    currency: str
    opening_balance: Decimal = Decimal("0.00")
    institution_name: str | None = None
    last_four: str | None = None


class CreateAccountCommand:
    def __init__(self, repository: AccountRepository) -> None:
        self._repository = repository

    def execute(self, data: CreateAccountInput) -> Account:
        account = Account.create(
            organization_id=data.organization_id,
            name=data.name,
            account_type=data.account_type,
            currency=data.currency,
            opening_balance=data.opening_balance,
            institution_name=data.institution_name,
            last_four=data.last_four,
        )
        return self._repository.add(account)
