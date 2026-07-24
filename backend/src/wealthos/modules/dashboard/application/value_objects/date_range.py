"""Inclusive consumer date range expressed as a half-open UTC interval."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from wealthos.modules.dashboard.domain.exceptions import InvalidDateRange


@dataclass(frozen=True, slots=True)
class DateRange:
    """Half-open UTC interval: start <= t < end_exclusive."""

    start: datetime
    end_exclusive: datetime
    display_from: date
    display_to: date
    timezone: str

    def __post_init__(self) -> None:
        if self.start >= self.end_exclusive:
            raise InvalidDateRange("date_from must be before or equal to date_to.")
        if self.start.tzinfo is None or self.end_exclusive.tzinfo is None:
            raise InvalidDateRange("DateRange bounds must be timezone-aware UTC.")
