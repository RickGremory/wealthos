"""Frequency strategies — emit base dates only."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Protocol

from wealthos.modules.recurring.domain.entities.recurring_rule_version import (
    RecurringRuleVersion,
)
from wealthos.modules.recurring.domain.enums.recurrence import RecurrenceFrequency
from wealthos.modules.recurring.domain.exceptions import UnsupportedRecurrenceFrequency
from wealthos.modules.recurring.domain.policies.date_math import (
    add_months,
    first_daily_occurrence_on_or_after,
    month_index,
    resolve_monthly_date,
    start_of_week,
)


class RecurrenceStrategy(Protocol):
    def generate_base_dates(
        self,
        *,
        version: RecurringRuleVersion,
        effective_start: date,
        effective_end: date,
    ) -> tuple[date, ...]: ...


class DailyRecurrenceStrategy:
    def generate_base_dates(
        self,
        *,
        version: RecurringRuleVersion,
        effective_start: date,
        effective_end: date,
    ) -> tuple[date, ...]:
        interval = version.pattern.interval
        anchor = version.starts_on
        current = first_daily_occurrence_on_or_after(
            anchor=anchor,
            target=effective_start,
            interval=interval,
        )
        if current < anchor:
            current = anchor
        dates: list[date] = []
        while current <= effective_end:
            if current >= anchor and (version.ends_on is None or current <= version.ends_on):
                dates.append(current)
            current += timedelta(days=interval)
        return tuple(dates)


class WeeklyRecurrenceStrategy:
    def generate_base_dates(
        self,
        *,
        version: RecurringRuleVersion,
        effective_start: date,
        effective_end: date,
    ) -> tuple[date, ...]:
        pattern = version.pattern
        interval = pattern.interval
        anchor_week = start_of_week(version.starts_on)
        current_week = start_of_week(effective_start)
        weeks_since = (current_week - anchor_week).days // 7
        if weeks_since < 0:
            current_week = anchor_week
            weeks_since = 0
        remainder = weeks_since % interval
        if remainder:
            current_week += timedelta(weeks=interval - remainder)

        dates: list[date] = []
        while current_week <= effective_end:
            for weekday in pattern.days_of_week:
                candidate = current_week + timedelta(days=int(weekday))
                if candidate < version.starts_on:
                    continue
                if version.ends_on is not None and candidate > version.ends_on:
                    continue
                if effective_start <= candidate <= effective_end:
                    dates.append(candidate)
            current_week += timedelta(weeks=interval)
        return tuple(dates)


class MonthlyRecurrenceStrategy:
    def generate_base_dates(
        self,
        *,
        version: RecurringRuleVersion,
        effective_start: date,
        effective_end: date,
    ) -> tuple[date, ...]:
        pattern = version.pattern
        interval = pattern.interval
        anchor = version.starts_on
        year, month = effective_start.year, effective_start.month
        # Align to first eligible month index relative to anchor month.
        while True:
            delta = month_index(date(year, month, 1)) - month_index(anchor)
            if delta >= 0 and delta % interval == 0:
                break
            if delta < 0:
                year, month = add_months(year=year, month=month, months=1)
                continue
            year, month = add_months(year=year, month=month, months=1)

        dates: list[date] = []
        while date(year, month, 1) <= effective_end:
            delta = month_index(date(year, month, 1)) - month_index(anchor)
            if delta >= 0 and delta % interval == 0:
                resolved = resolve_monthly_date(
                    year=year,
                    month=month,
                    pattern=pattern,
                    invalid_date_policy=pattern.invalid_date_policy,
                )
                if resolved is not None:
                    if resolved < version.starts_on:
                        pass
                    elif version.ends_on is not None and resolved > version.ends_on:
                        pass
                    elif effective_start <= resolved <= effective_end:
                        dates.append(resolved)
            year, month = add_months(year=year, month=month, months=interval)
        return tuple(dates)


class YearlyRecurrenceStrategy:
    def generate_base_dates(
        self,
        *,
        version: RecurringRuleVersion,
        effective_start: date,
        effective_end: date,
    ) -> tuple[date, ...]:
        pattern = version.pattern
        interval = pattern.interval
        assert pattern.month_of_year is not None
        year = effective_start.year
        while (year - version.starts_on.year) % interval != 0 or year < version.starts_on.year:
            year += 1
            if year > effective_end.year + 1:
                return ()

        dates: list[date] = []
        while year <= effective_end.year:
            if (year - version.starts_on.year) % interval == 0:
                resolved = resolve_monthly_date(
                    year=year,
                    month=pattern.month_of_year,
                    pattern=pattern,
                    invalid_date_policy=pattern.invalid_date_policy,
                )
                if resolved is not None:
                    if resolved < version.starts_on:
                        pass
                    elif version.ends_on is not None and resolved > version.ends_on:
                        pass
                    elif effective_start <= resolved <= effective_end:
                        dates.append(resolved)
            year += interval
        return tuple(dates)


def strategy_for(frequency: RecurrenceFrequency) -> RecurrenceStrategy:
    mapping: dict[RecurrenceFrequency, RecurrenceStrategy] = {
        RecurrenceFrequency.DAILY: DailyRecurrenceStrategy(),
        RecurrenceFrequency.WEEKLY: WeeklyRecurrenceStrategy(),
        RecurrenceFrequency.MONTHLY: MonthlyRecurrenceStrategy(),
        RecurrenceFrequency.YEARLY: YearlyRecurrenceStrategy(),
    }
    try:
        return mapping[frequency]
    except KeyError as exc:
        raise UnsupportedRecurrenceFrequency(
            f"Unsupported frequency: {frequency}"
        ) from exc
