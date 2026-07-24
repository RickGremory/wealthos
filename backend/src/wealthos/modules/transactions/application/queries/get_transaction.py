"""GetTransaction query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.modules.transactions.domain.exceptions import TransactionNotFoundError
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionRepository,
)


class GetTransactionQuery:
    def __init__(self, repository: TransactionRepository) -> None:
        self._repository = repository

    def execute(self, organization_id: UUID, transaction_id: UUID) -> Transaction:
        transaction = self._repository.get_by_id(organization_id, transaction_id)
        if transaction is None:
            raise TransactionNotFoundError("Transaction not found.")
        return transaction
