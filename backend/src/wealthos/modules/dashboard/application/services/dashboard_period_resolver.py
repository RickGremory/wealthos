"""Resolve dashboard period presets into UTC DateRange values."""

from __future__ import annotations

from calendar import monthrange
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from wealthos.modules.dashboard.application.value_objects.date_range import DateRange
from wealthos.modules.dashboard.domain.exceptions import (
    CustomPeriodRequiresDates,
    InvalidDateRange,
)
from wealthos.modules.dashboard.domain.value_objects.dashboard_period import (
    DashboardPeriod,
)


class DashboardPeriodResolver:
    """Convert local calendar periods into half-open UTC intervals."""

    def resolve(
        self,
        *,
        period: DashboardPeriod | str,
        timezone: str,
        date_from: date | None = None,
        date_to: date | None = None,
        today: date | None = None,
    ) -> DateRange:
        period_vo = period if isinstance(period, DashboardPeriod) else DashboardPeriod(period)
        tz = ZoneInfo(timezone)
        local_today = today or datetime.now(tz).date()

        if period_vo.is_custom:
            if date_from is None or date_to is None:
                raise CustomPeriodRequiresDates("custom period requires date_from and date_to.")
            start_local = date_from
            end_local = date_to
        elif period_vo.value == "this_month":
            start_local = local_today.replace(day=1)
            end_local = local_today
        elif period_vo.value == "last_month":
            first_this_month = local_today.replace(day=1)
            last_day_prev = first_this_month - timedelta(days=1)
            start_local = last_day_prev.replace(day=1)
            end_local = last_day_prev
        elif period_vo.value == "last_30_days":
            end_local = local_today
            start_local = local_today - timedelta(days=29)
        elif period_vo.value == "this_year":
            start_local = date(local_today.year, 1, 1)
            end_local = local_today
        else:
            raise InvalidDateRange(f"Unsupported period: {period_vo.value}")

        if start_local > end_local:
            raise InvalidDateRange("date_from must be on or before date_to.")

        start_utc = datetime(
            start_local.year,
            start_local.month,
            start_local.day,
            tzinfo=tz,
        ).astimezone(UTC)
        # Inclusive date_to → exclusive next local midnight.
        end_exclusive_local = end_local + timedelta(days=1)
        end_utc = datetime(
            end_exclusive_local.year,
            end_exclusive_local.month,
            end_exclusive_local.day,
            tzinfo=tz,
        ).astimezone(UTC)

        return DateRange(
            start=start_utc,
            end_exclusive=end_utc,
            display_from=start_local,
            display_to=end_local,
            timezone=timezone,
        )

    @staticmethod
    def days_in_month(year: int, month: int) -> int:
        return monthrange(year, month)[1]
