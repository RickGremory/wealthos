"""Same-day ordering: survive the outflow before trusting the inflow (§28)."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime

from wealthos.modules.planning.domain.enums.cash_flow import (
    CashFlowCertainty,
    CashFlowDirection,
)
from wealthos.modules.planning.domain.value_objects.cash_flow import PlanningCashFlow

_CERTAINTY_RANK: dict[CashFlowCertainty, int] = {
    CashFlowCertainty.CONFIRMED: 0,
    CashFlowCertainty.EXPECTED: 1,
    CashFlowCertainty.ESTIMATED: 2,
}


def event_priority(flow: PlanningCashFlow) -> int:
    """Outflows (0–2) always run before inflows (10–12) on the same day."""
    base = 0 if flow.direction is CashFlowDirection.OUTFLOW else 10
    return base + _CERTAINTY_RANK[flow.certainty]


def event_sort_key(flow: PlanningCashFlow) -> tuple[date, int, datetime, str, str]:
    """Day granularity first: times are rarely trustworthy in forecasts."""
    return (
        flow.expected_at.date(),
        event_priority(flow),
        flow.expected_at,
        flow.occurrence_key,
        flow.id,
    )


def order_events(flows: Iterable[PlanningCashFlow]) -> tuple[PlanningCashFlow, ...]:
    return tuple(sorted(flows, key=event_sort_key))
