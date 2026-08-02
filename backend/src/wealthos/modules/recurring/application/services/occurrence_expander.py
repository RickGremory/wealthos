"""Expand occurrences for one aggregate across versions in a period."""

from __future__ import annotations

from datetime import date
from typing import Sequence

from wealthos.modules.recurring.domain.entities.occurrence_settlement import (
    RecurringOccurrenceSettlement,
)
from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
)
from wealthos.modules.recurring.domain.services.recurrence_generator import (
    DefaultRecurrenceGenerator,
)
from wealthos.modules.recurring.domain.value_objects.recurring_occurrence import (
    RecurringOccurrence,
)


class RecurringOccurrenceExpander:
    def __init__(self, generator: DefaultRecurrenceGenerator | None = None) -> None:
        self._generator = generator or DefaultRecurrenceGenerator()

    def expand(
        self,
        aggregate: RecurringAggregate,
        *,
        period_start: date,
        period_end: date,
        evaluated_on: date,
        timezone: str,
        settlements: Sequence[RecurringOccurrenceSettlement] = (),
        currency: str | None = None,
    ) -> tuple[RecurringOccurrence, ...]:
        results: list[RecurringOccurrence] = []
        versions = aggregate.versions_affecting(period_start, period_end)
        for version in versions:
            if currency is not None and version.currency.upper() != currency.upper():
                continue
            clip_start = max(period_start, version.effective_from, version.starts_on)
            clip_end = period_end
            if version.effective_until is not None:
                clip_end = min(clip_end, version.effective_until)
            if version.ends_on is not None:
                clip_end = min(clip_end, version.ends_on)
            if clip_start > clip_end:
                continue
            results.extend(
                self._generator.generate(
                    rule=aggregate.rule,
                    version=version,
                    period_start=clip_start,
                    period_end=clip_end,
                    pauses=tuple(aggregate.pauses),
                    exceptions=tuple(aggregate.active_exceptions()),
                    settlements=settlements,
                    evaluated_on=evaluated_on,
                    timezone=timezone,
                )
            )
        return tuple(
            sorted(results, key=lambda item: (item.expected_on, item.occurrence_key.value))
        )
