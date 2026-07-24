"""Goal progress projection (derived, not persisted)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class GoalProgress:
    goal_id: UUID
    current_amount: Money
    remaining_amount: Money
    completion_percentage: Decimal
    estimated_completion_date: date | None
