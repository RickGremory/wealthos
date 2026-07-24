"""Cash-flow series views."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CashFlowPointView:
    period_start: date
    income: Decimal
    expenses: Decimal
    net_cash_flow: Decimal


@dataclass(frozen=True, slots=True)
class CashFlowSeriesView:
    currency: str
    items: tuple[CashFlowPointView, ...]
