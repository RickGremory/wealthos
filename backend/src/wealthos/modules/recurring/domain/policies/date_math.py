"""Date arithmetic helpers for recurrence strategies."""

from __future__ import annotations

import calendar
from datetime import date, timedelta

from wealthos.modules.recurring.domain.enums.recurrence import InvalidDatePolicy
from wealthos.modules.recurring.domain.exceptions import UnsupportedInvalidDatePolicy
from wealthos.modules.recurring.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)


def start_of_week(value: date) -> date:
    return value - timedelta(days=value.weekday())


def month_index(value: date) -> int:
    return value.year * 12 + value.month - 1


def add_months(*, year: int, month: int, months: int) -> tuple[int, int]:
    absolute = year * 12 + (month - 1) + months
    next_year, zero_based = divmod(absolute, 12)
    return next_year, zero_based + 1


def first_daily_occurrence_on_or_after(
    *,
    anchor: date,
    target: date,
    interval: int,
) -> date:
    if target <= anchor:
        return anchor
    elapsed = (target - anchor).days
    remainder = elapsed % interval
    if remainder == 0:
        return target
    return target + timedelta(days=interval - remainder)


def resolve_monthly_date(
    *,
    year: int,
    month: int,
    pattern: RecurrencePattern,
    invalid_date_policy: InvalidDatePolicy,
) -> date | None:
    last_day = calendar.monthrange(year, month)[1]
    if pattern.end_of_month:
        return date(year, month, last_day)
    requested = pattern.day_of_month
    assert requested is not None
    if requested <= last_day:
        return date(year, month, requested)
    if invalid_date_policy is InvalidDatePolicy.LAST_DAY_OF_MONTH:
        return date(year, month, last_day)
    if invalid_date_policy is InvalidDatePolicy.SKIP_OCCURRENCE:
        return None
    raise UnsupportedInvalidDatePolicy(f"Unsupported policy: {invalid_date_policy}")
