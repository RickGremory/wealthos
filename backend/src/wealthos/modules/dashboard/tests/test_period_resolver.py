"""Dashboard period resolver tests."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from wealthos.modules.dashboard.application.services.dashboard_period_resolver import (
    DashboardPeriodResolver,
)
from wealthos.modules.dashboard.domain.exceptions import (
    CustomPeriodRequiresDates,
    InvalidDateRange,
)
from wealthos.modules.dashboard.domain.value_objects.dashboard_period import (
    DashboardPeriod,
)


def test_this_month_and_timezone_conversion() -> None:
    resolver = DashboardPeriodResolver()
    result = resolver.resolve(
        period="this_month",
        timezone="America/Cancun",
        today=date(2026, 7, 15),
    )
    assert result.display_from == date(2026, 7, 1)
    assert result.display_to == date(2026, 7, 15)
    assert result.start == datetime(2026, 7, 1, 5, 0, tzinfo=UTC)
    assert result.end_exclusive == datetime(2026, 7, 16, 5, 0, tzinfo=UTC)


def test_last_month_crosses_year() -> None:
    resolver = DashboardPeriodResolver()
    result = resolver.resolve(
        period="last_month",
        timezone="America/Cancun",
        today=date(2026, 1, 10),
    )
    assert result.display_from == date(2025, 12, 1)
    assert result.display_to == date(2025, 12, 31)


def test_this_year_and_last_30_days() -> None:
    resolver = DashboardPeriodResolver()
    year = resolver.resolve(
        period="this_year",
        timezone="UTC",
        today=date(2026, 7, 23),
    )
    assert year.display_from == date(2026, 1, 1)
    assert year.display_to == date(2026, 7, 23)

    days = resolver.resolve(
        period="last_30_days",
        timezone="UTC",
        today=date(2026, 7, 23),
    )
    assert days.display_from == date(2026, 6, 24)
    assert days.display_to == date(2026, 7, 23)
    assert (days.display_to - days.display_from).days == 29


def test_custom_requires_dates_and_rejects_inverted() -> None:
    resolver = DashboardPeriodResolver()
    with pytest.raises(CustomPeriodRequiresDates):
        resolver.resolve(period=DashboardPeriod("custom"), timezone="UTC")

    with pytest.raises(InvalidDateRange):
        resolver.resolve(
            period="custom",
            timezone="UTC",
            date_from=date(2026, 7, 31),
            date_to=date(2026, 7, 1),
        )

    custom = resolver.resolve(
        period="custom",
        timezone="America/Cancun",
        date_from=date(2026, 7, 1),
        date_to=date(2026, 7, 31),
    )
    assert custom.display_from == date(2026, 7, 1)
    assert custom.display_to == date(2026, 7, 31)
    assert custom.end_exclusive == datetime(2026, 8, 1, 5, 0, tzinfo=UTC)


def test_leap_year_february() -> None:
    resolver = DashboardPeriodResolver()
    result = resolver.resolve(
        period="custom",
        timezone="UTC",
        date_from=date(2024, 2, 1),
        date_to=date(2024, 2, 29),
    )
    assert result.display_to == date(2024, 2, 29)
    assert result.end_exclusive.date() == date(2024, 3, 1)
