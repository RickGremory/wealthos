"""GetDebtActivityQuery — transactions on the linked liability account."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.debts.domain.exceptions import DebtNotFoundError
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionFilters,
    TransactionRepository,
)


@dataclass(frozen=True, slots=True)
class DebtActivityResult:
    items: list[Transaction]
    total: int
    limit: int
    offset: int


class GetDebtActivityQuery:
    def __init__(
        self,
        debts: DebtRepository,
        transactions: TransactionRepository,
    ) -> None:
        self._debts = debts
        self._transactions = transactions

    def execute(
        self,
        organization_id: UUID,
        debt_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> DebtActivityResult:
        debt = self._debts.get_by_id(organization_id, debt_id)
        if debt is None:
            raise DebtNotFoundError("Debt not found.")

        result = self._transactions.list_by_organization(
            organization_id,
            TransactionFilters(
                account_id=debt.account_id,
                limit=limit,
                offset=offset,
            ),
        )
        return DebtActivityResult(
            items=result.items,
            total=result.total,
            limit=limit,
            offset=offset,
        )
