"""Create transfer transaction command."""

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
class CreateTransferInput:
    organization_id: UUID
    source_account_id: UUID
    destination_account_id: UUID
    amount: Decimal
    description: str
    occurred_at: datetime
    created_by_user_id: UUID
    notes: str | None = None


class CreateTransferCommand:
    def __init__(
        self,
        posting: TransactionPostingService,
        accounts: AccountRepository,
    ) -> None:
        self._posting = posting
        self._accounts = accounts

    def execute(self, data: CreateTransferInput) -> Transaction:
        source = self._accounts.get_by_id(
            data.organization_id,
            data.source_account_id,
        )
        if source is None:
            raise AccountNotFoundError("Source account not found.")
        destination = self._accounts.get_by_id(
            data.organization_id,
            data.destination_account_id,
        )
        if destination is None:
            raise AccountNotFoundError("Destination account not found.")
        transaction = Transaction.create_transfer(
            organization_id=data.organization_id,
            source_account_id=data.source_account_id,
            destination_account_id=data.destination_account_id,
            amount=Money(data.amount, source.currency),
            description=data.description,
            occurred_at=data.occurred_at,
            created_by_user_id=data.created_by_user_id,
            notes=data.notes,
        )
        return self._posting.post(transaction)
