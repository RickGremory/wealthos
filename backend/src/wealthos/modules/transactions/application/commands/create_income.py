"""Create income transaction command."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.transactions.application.services.transaction_posting_service import (
    TransactionPostingService,
)
from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.modules.transactions.domain.exceptions import AccountNotFoundError
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class CreateIncomeInput:
    organization_id: UUID
    account_id: UUID
    category_id: UUID
    amount: Decimal
    description: str
    occurred_at: datetime
    created_by_user_id: UUID
    notes: str | None = None


class CreateIncomeCommand:
    def __init__(
        self,
        posting: TransactionPostingService,
        accounts: AccountRepository,
    ) -> None:
        self._posting = posting
        self._accounts = accounts

    def execute(self, data: CreateIncomeInput) -> Transaction:
        account = self._accounts.get_by_id(data.organization_id, data.account_id)
        if account is None:
            raise AccountNotFoundError("Account not found.")
        transaction = Transaction.create_income(
            organization_id=data.organization_id,
            account_id=data.account_id,
            category_id=data.category_id,
            amount=Money(data.amount, account.currency),
            description=data.description,
            occurred_at=data.occurred_at,
            created_by_user_id=data.created_by_user_id,
            notes=data.notes,
        )
        return self._posting.post(transaction)
