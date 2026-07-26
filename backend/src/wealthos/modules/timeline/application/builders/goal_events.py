"""Build FinancialEvents from goals lifecycle and milestones."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from wealthos.shared.events import FinancialEvent

MILESTONE_THRESHOLDS = (25, 50, 75, 100)


def build_goal_created_event(
    *,
    organization_id: UUID,
    goal_id: UUID,
    name: str,
    occurred_at: datetime,
    currency: str,
    target_amount: Decimal,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="goal",
        event_type="goal.created",
        importance="high",
        title="Nueva meta",
        description=f"Se creó la meta «{name}».",
        resource_type="goal",
        resource_id=goal_id,
        currency=currency,
        amount=target_amount,
        metadata={"name": name},
    )


def build_goal_milestone_event(
    *,
    organization_id: UUID,
    goal_id: UUID,
    name: str,
    occurred_at: datetime,
    currency: str,
    percent: int,
    current_amount: Decimal | None = None,
) -> FinancialEvent:
    event_type = f"goal.milestone_{percent}"
    if percent >= 100:
        title = "Meta completada"
        description = f"«{name}» alcanzó el 100%."
        importance = "critical"
    else:
        title = f"Meta al {percent}%"
        description = f"«{name}» alcanzó el {percent}% de avance."
        importance = "high"
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="goal",
        event_type=event_type,
        importance=importance,  # type: ignore[arg-type]
        title=title,
        description=description,
        resource_type="goal",
        resource_id=goal_id,
        currency=currency,
        amount=current_amount,
        metadata={"name": name, "percent": percent},
    )


def build_goal_completed_event(
    *,
    organization_id: UUID,
    goal_id: UUID,
    name: str,
    occurred_at: datetime,
    currency: str,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="goal",
        event_type="goal.completed",
        importance="critical",
        title="Meta completada",
        description=f"«{name}» se marcó como completada.",
        resource_type="goal",
        resource_id=goal_id,
        currency=currency,
        metadata={"name": name},
    )


def crossed_milestones(
    previous_percent: float,
    current_percent: float,
) -> list[int]:
    """Return milestone thresholds newly crossed (exclusive of previous)."""
    crossed: list[int] = []
    for threshold in MILESTONE_THRESHOLDS:
        if previous_percent < threshold <= current_percent:
            crossed.append(threshold)
    return crossed
