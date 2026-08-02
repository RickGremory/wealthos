"""Normalize and query pause windows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Sequence

from wealthos.modules.recurring.domain.entities.recurring_rule_pause import (
    RecurringRulePause,
)


@dataclass(frozen=True, slots=True)
class DateRange:
    starts_on: date
    ends_on: date | None

    def contains(self, value: date) -> bool:
        if value < self.starts_on:
            return False
        if self.ends_on is None:
            return True
        return value <= self.ends_on


class PauseNormalizer:
    def normalize(
        self,
        pauses: Sequence[RecurringRulePause],
    ) -> tuple[DateRange, ...]:
        if not pauses:
            return ()
        ordered = sorted(pauses, key=lambda item: item.starts_on)
        merged: list[DateRange] = []
        for pause in ordered:
            current = DateRange(pause.starts_on, pause.ends_on)
            if not merged:
                merged.append(current)
                continue
            last = merged[-1]
            if last.ends_on is None:
                continue
            # Adjacent or overlapping → merge
            if current.starts_on <= last.ends_on + timedelta(days=1):
                if current.ends_on is None:
                    merged[-1] = DateRange(last.starts_on, None)
                else:
                    merged[-1] = DateRange(
                        last.starts_on,
                        max(last.ends_on, current.ends_on),
                    )
            else:
                merged.append(current)
        return tuple(merged)

    def contains(self, ranges: Sequence[DateRange], value: date) -> bool:
        return any(item.contains(value) for item in ranges)
