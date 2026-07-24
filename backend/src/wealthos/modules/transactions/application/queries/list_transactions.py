"""ListTransactions query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionFilters,
    TransactionListResult,
    TransactionRepository,
)


class ListTransactionsQuery:
    def __init__(self, repository: TransactionRepository) -> None:
        self._repository = repository

    def execute(
        self,
        organization_id: UUID,
        filters: TransactionFilters,
    ) -> TransactionListResult:
        return self._repository.list_by_organization(organization_id, filters)
