"""Deduplicate planning commitments by source priority."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

_PRIORITY: dict[str, int] = {
    "matched_transaction": 100,
    "confirmed_cash_plan_item": 80,
    "planned_cash_plan_item": 60,
    "linked_module_recommendation": 40,
    "budget_allocation": 20,
}


@dataclass(frozen=True, slots=True)
class PlanningCommitment:
    source: str
    amount: Decimal
    expected_date: date | None = None
    currency: str | None = None
    linked_entity_type: str | None = None
    linked_entity_id: UUID | None = None
    debt_id: UUID | None = None
    tax_period_id: UUID | None = None
    goal_id: UUID | None = None
    cash_plan_item_id: UUID | None = None
    description: str | None = None
    archived: bool = False
    cancelled: bool = False


class PlanningCommitmentResolver:
    """Keep the highest-priority representation per logical commitment key."""

    def resolve(
        self,
        commitments: tuple[PlanningCommitment, ...] | list[PlanningCommitment],
    ) -> tuple[PlanningCommitment, ...]:
        winners: dict[tuple[str, str], PlanningCommitment] = {}

        for item in commitments:
            if item.archived or item.cancelled:
                continue
            key = _dedupe_key(item)
            if key is None:
                # Unkeyed commitments always pass through (no collision possible).
                winners[("unique", str(id(item)))] = item
                continue

            existing = winners.get(key)
            if existing is None or _priority(item.source) > _priority(existing.source):
                winners[key] = item

        return tuple(winners.values())


def _dedupe_key(item: PlanningCommitment) -> tuple[str, str] | None:
    if item.linked_entity_type and item.linked_entity_id is not None:
        return (item.linked_entity_type, str(item.linked_entity_id))
    if item.debt_id is not None:
        return ("debt", str(item.debt_id))
    if item.tax_period_id is not None:
        return ("tax_period", str(item.tax_period_id))
    if item.goal_id is not None:
        return ("goal", str(item.goal_id))
    return None


def _priority(source: str) -> int:
    return _PRIORITY.get(source.strip().lower(), 0)
