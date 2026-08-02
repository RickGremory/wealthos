"""RecurrencePattern value object (SPEC-005 / Sprint 9.1–9.2)."""

from __future__ import annotations

from dataclasses import dataclass

from wealthos.modules.recurring.domain.enums.recurrence import (
    InvalidDatePolicy,
    RecurrenceFrequency,
    Weekday,
)
from wealthos.modules.recurring.domain.exceptions import InvalidRecurrencePattern


@dataclass(frozen=True, slots=True)
class RecurrencePattern:
    frequency: RecurrenceFrequency
    interval: int
    days_of_week: tuple[Weekday, ...] = ()
    day_of_month: int | None = None
    month_of_year: int | None = None
    end_of_month: bool = False
    invalid_date_policy: InvalidDatePolicy = InvalidDatePolicy.LAST_DAY_OF_MONTH

    def __post_init__(self) -> None:
        if self.interval < 1:
            raise InvalidRecurrencePattern("interval must be >= 1.")

        object.__setattr__(
            self,
            "days_of_week",
            tuple(sorted(set(self.days_of_week), key=lambda day: int(day))),
        )

        freq = self.frequency
        if freq is RecurrenceFrequency.DAILY:
            self._forbid_weekly_monthly_yearly_fields()
            return

        if freq is RecurrenceFrequency.WEEKLY:
            if not self.days_of_week:
                raise InvalidRecurrencePattern(
                    "Weekly patterns require at least one day_of_week."
                )
            if self.day_of_month is not None or self.month_of_year is not None:
                raise InvalidRecurrencePattern(
                    "Weekly patterns cannot set day_of_month or month_of_year."
                )
            if self.end_of_month:
                raise InvalidRecurrencePattern(
                    "Weekly patterns cannot set end_of_month."
                )
            return

        if freq is RecurrenceFrequency.MONTHLY:
            self._require_monthly_day_choice()
            if self.days_of_week:
                raise InvalidRecurrencePattern(
                    "Monthly patterns cannot set days_of_week."
                )
            if self.month_of_year is not None:
                raise InvalidRecurrencePattern(
                    "Monthly patterns cannot set month_of_year."
                )
            return

        if freq is RecurrenceFrequency.YEARLY:
            if self.month_of_year is None or not (1 <= self.month_of_year <= 12):
                raise InvalidRecurrencePattern(
                    "Yearly patterns require month_of_year between 1 and 12."
                )
            self._require_monthly_day_choice()
            if self.days_of_week:
                raise InvalidRecurrencePattern(
                    "Yearly patterns cannot set days_of_week."
                )
            return

        raise InvalidRecurrencePattern(f"Unsupported frequency: {freq}.")

    def _forbid_weekly_monthly_yearly_fields(self) -> None:
        if self.days_of_week:
            raise InvalidRecurrencePattern("Daily patterns cannot set days_of_week.")
        if self.day_of_month is not None:
            raise InvalidRecurrencePattern("Daily patterns cannot set day_of_month.")
        if self.month_of_year is not None:
            raise InvalidRecurrencePattern("Daily patterns cannot set month_of_year.")
        if self.end_of_month:
            raise InvalidRecurrencePattern("Daily patterns cannot set end_of_month.")

    def _require_monthly_day_choice(self) -> None:
        has_day = self.day_of_month is not None
        if has_day and self.end_of_month:
            raise InvalidRecurrencePattern(
                "Provide exactly one of day_of_month or end_of_month."
            )
        if not has_day and not self.end_of_month:
            raise InvalidRecurrencePattern(
                "Provide exactly one of day_of_month or end_of_month."
            )
        if has_day and not (1 <= int(self.day_of_month) <= 31):  # type: ignore[arg-type]
            raise InvalidRecurrencePattern("day_of_month must be between 1 and 31.")
