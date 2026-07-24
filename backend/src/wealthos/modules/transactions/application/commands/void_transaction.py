"""Void transaction command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.transactions.application.services.transaction_posting_service import (
    TransactionPostingService,
)
from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.modules.transactions.domain.exceptions import TransactionNotFoundError
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionRepository,
)


@dataclass(frozen=True, slots=True)
class VoidTransactionInput:
    organization_id: UUID
    transaction_id: UUID
    voided_by_user_id: UUID


class VoidTransactionCommand:
    def __init__(
        self,
        repository: TransactionRepository,
        posting: TransactionPostingService,
    ) -> None:
        self._repository = repository
        self._posting = posting

    def execute(self, data: VoidTransactionInput) -> Transaction:
        transaction = self._repository.get_by_id(
            data.organization_id,
            data.transaction_id,
        )
        if transaction is None:
            raise TransactionNotFoundError("Transaction not found.")
        return self._posting.void(
            transaction,
            voided_by_user_id=data.voided_by_user_id,
        )
