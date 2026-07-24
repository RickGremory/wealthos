"""Shared dashboard period filter payload."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from wealthos.modules.dashboard.domain.value_objects.dashboard_period import (
    DashboardPeriod,
)


@dataclass(frozen=True, slots=True)
class DashboardPeriodFilters:
    period: DashboardPeriod
    date_from: date | None = None
    date_to: date | None = None
