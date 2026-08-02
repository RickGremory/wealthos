"""Inclusive date range helpers for version / pause validity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from wealthos.modules.recurring.domain.exceptions import InvalidEffectiveDate


@dataclass(frozen=True, slots=True)
class EffectivePeriod:
    start: date
    end: date | None  # None = open-ended

    def __post_init__(self) -> None:
        if self.end is not None and self.end < self.start:
            raise InvalidEffectiveDate("effective end cannot precede start.")

    def overlaps(self, other: EffectivePeriod) -> bool:
        other_end = other.end or date.max
        self_end = self.end or date.max
        return self.start <= other_end and other.start <= self_end

    def contains(self, value: date) -> bool:
        if value < self.start:
            return False
        if self.end is None:
            return True
        return value <= self.end
