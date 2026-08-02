"""Recurrence frequency and invalid-date policy."""

from __future__ import annotations

from enum import IntEnum, StrEnum

from wealthos.modules.recurring.domain.exceptions import InvalidRecurrencePattern, RecurringError


class RecurrenceFrequency(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

    @classmethod
    def parse(cls, value: str | RecurrenceFrequency) -> RecurrenceFrequency:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            allowed = ", ".join(member.value for member in cls)
            raise InvalidRecurrencePattern(
                f"Frequency must be one of: {allowed}."
            ) from exc


class InvalidDatePolicy(StrEnum):
    LAST_DAY_OF_MONTH = "last_day_of_month"
    SKIP_OCCURRENCE = "skip_occurrence"

    @classmethod
    def parse(cls, value: str | InvalidDatePolicy) -> InvalidDatePolicy:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            allowed = ", ".join(member.value for member in cls)
            raise RecurringError(
                f"Invalid date policy must be one of: {allowed}.",
                code="unsupported_invalid_date_policy",
            ) from exc


class Weekday(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @classmethod
    def parse(cls, value: int | Weekday | str) -> Weekday:
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            return cls(value)
        normalized = str(value).strip().lower()
        by_name = {member.name.lower(): member for member in cls}
        if normalized in by_name:
            return by_name[normalized]
        try:
            return cls(int(normalized))
        except (TypeError, ValueError) as exc:
            raise InvalidRecurrencePattern(f"Invalid weekday: {value!r}.") from exc
