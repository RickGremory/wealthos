"""Recent transaction projection views."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class NamedRefView:
    id: UUID
    name: str


@dataclass(frozen=True, slots=True)
class RecentTransactionView:
    id: UUID
    transaction_type: str
    description: str
    category: NamedRefView | None
    occurred_at: datetime
    status: str
    amount: Decimal
    currency: str
    account: NamedRefView | None
    source_account: NamedRefView | None
    destination_account: NamedRefView | None
