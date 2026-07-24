"""Read-model views for planning queries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CategoryActualView:
    category_id: UUID | None
    allocation_type: str
    actual_amount: Decimal


@dataclass(frozen=True, slots=True)
class BudgetActualsView:
    budget_id: UUID
    currency: str
    date_from: date
    date_to: date
    income_actual: Decimal
    expense_actual: Decimal
    by_category: tuple[CategoryActualView, ...]


@dataclass(frozen=True, slots=True)
class LiquidAccountBalanceView:
    account_id: UUID
    account_type: str
    currency: str
    current_balance: Decimal


@dataclass(frozen=True, slots=True)
class PlanningCommitmentView:
    source: str
    source_id: UUID
    description: str
    expected_date: date
    amount: Decimal
    currency: str
    linked_entity_type: str | None
    linked_entity_id: UUID | None
    priority: int
