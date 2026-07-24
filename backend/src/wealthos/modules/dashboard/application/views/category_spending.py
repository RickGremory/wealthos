"""Category spending views."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CategorySpendingItemView:
    category_id: UUID
    category_name: str
    amount: Decimal
    percentage: Decimal
    transaction_count: int


@dataclass(frozen=True, slots=True)
class CategorySpendingSeriesView:
    currency: str
    total_expenses: Decimal
    items: tuple[CategorySpendingItemView, ...]
