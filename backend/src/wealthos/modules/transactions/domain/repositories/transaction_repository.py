"""Persistence port for Transaction aggregates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from wealthos.modules.transactions.domain.entities.transaction import Transaction


@dataclass(frozen=True, slots=True)
class TransactionFilters:
    account_id: UUID | None = None
    category_id: UUID | None = None
    transaction_type: str | None = None
    status: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    search: str | None = None
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True, slots=True)
class TransactionListResult:
    items: list[Transaction]
    total: int


class TransactionRepository(Protocol):
    def add(self, transaction: Transaction) -> Transaction: ...

    def get_by_id(
        self,
        organization_id: UUID,
        transaction_id: UUID,
    ) -> Transaction | None: ...

    def list_by_organization(
        self,
        organization_id: UUID,
        filters: TransactionFilters,
    ) -> TransactionListResult: ...

    def save(self, transaction: Transaction) -> Transaction: ...
