"""Shared occurrence projection for Planning / Calendar / Dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.recurring.application.services.occurrence_expander import (
    RecurringOccurrenceExpander,
)
from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
)
from wealthos.modules.recurring.domain.enums.occurrence import RecurringOccurrenceStatus
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringDirection,
    RecurringRuleStatus,
)
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringAggregateRepository,
    RecurringRuleFilters,
    RecurringSettlementRepository,
)
from wealthos.modules.recurring.domain.value_objects.recurring_occurrence import (
    RecurringOccurrence,
)

_OPEN_STATUSES = frozenset(
    {
        RecurringOccurrenceStatus.UPCOMING,
        RecurringOccurrenceStatus.DUE,
        RecurringOccurrenceStatus.OVERDUE,
        RecurringOccurrenceStatus.PARTIALLY_SETTLED,
    }
)


@dataclass(frozen=True, slots=True)
class ProjectedRecurringOccurrence:
    """Occurrence ready for consumer adapters (Planning / Calendar / Dashboard)."""

    occurrence: RecurringOccurrence
    name: str
    rule_version: int
    outstanding_amount: Decimal

    @property
    def occurrence_key(self) -> str:
        return self.occurrence.occurrence_key.value

    @property
    def direction(self) -> RecurringDirection:
        return self.occurrence.direction

    @property
    def status(self) -> RecurringOccurrenceStatus:
        return self.occurrence.status


class RecurringOccurrenceProjector:
    """Expand open, manually owned occurrences for a period (no N+1 settlements)."""

    def __init__(
        self,
        repo: RecurringAggregateRepository,
        settlements: RecurringSettlementRepository | None = None,
        expander: RecurringOccurrenceExpander | None = None,
    ) -> None:
        self._repo = repo
        self._settlements = settlements
        self._expander = expander or RecurringOccurrenceExpander()

    def project(
        self,
        *,
        organization_id: UUID,
        period_start: date,
        period_end: date,
        evaluated_on: date,
        timezone: str,
        currency: str | None = None,
        include_externally_managed: bool = False,
        include_transfers: bool = False,
    ) -> tuple[ProjectedRecurringOccurrence, ...]:
        aggregates = self._repo.list_aggregates(
            organization_id,
            RecurringRuleFilters(
                include_archived=False,
                currency=currency,
            ),
        )
        results: list[ProjectedRecurringOccurrence] = []
        for aggregate in aggregates:
            if aggregate.rule.status in {
                RecurringRuleStatus.ARCHIVED,
                RecurringRuleStatus.ENDED,
            }:
                continue
            if (
                not include_externally_managed
                and aggregate.rule.is_managed_externally
            ):
                continue
            results.extend(
                self._project_aggregate(
                    aggregate,
                    period_start=period_start,
                    period_end=period_end,
                    evaluated_on=evaluated_on,
                    timezone=timezone,
                    currency=currency,
                    include_transfers=include_transfers,
                )
            )
        results.sort(
            key=lambda item: (
                item.occurrence.expected_on,
                item.occurrence_key,
            )
        )
        return tuple(results)

    def _project_aggregate(
        self,
        aggregate: RecurringAggregate,
        *,
        period_start: date,
        period_end: date,
        evaluated_on: date,
        timezone: str,
        currency: str | None,
        include_transfers: bool,
    ) -> list[ProjectedRecurringOccurrence]:
        occurrences = self._expander.expand(
            aggregate,
            period_start=period_start,
            period_end=period_end,
            evaluated_on=evaluated_on,
            timezone=timezone,
            currency=currency,
        )
        if self._settlements is not None and occurrences:
            keys = tuple(item.occurrence_key.value for item in occurrences)
            settlements = tuple(
                self._settlements.list_for_keys(aggregate.organization_id, keys)
            )
            occurrences = self._expander.expand(
                aggregate,
                period_start=period_start,
                period_end=period_end,
                evaluated_on=evaluated_on,
                timezone=timezone,
                currency=currency,
                settlements=settlements,
            )

        current = aggregate.current_version(evaluated_on) or (
            aggregate.versions_tuple()[-1] if aggregate.versions else None
        )
        name = current.name if current else "Recurring"
        projected: list[ProjectedRecurringOccurrence] = []
        for occurrence in occurrences:
            if occurrence.status not in _OPEN_STATUSES:
                continue
            if (
                not include_transfers
                and occurrence.direction is RecurringDirection.TRANSFER
            ):
                continue
            outstanding = _outstanding_amount(occurrence)
            if outstanding <= Decimal("0"):
                continue
            projected.append(
                ProjectedRecurringOccurrence(
                    occurrence=occurrence,
                    name=name,
                    rule_version=aggregate.rule.version,
                    outstanding_amount=outstanding,
                )
            )
        return projected


def _outstanding_amount(occurrence: RecurringOccurrence) -> Decimal:
    if occurrence.status is RecurringOccurrenceStatus.PARTIALLY_SETTLED:
        actual = occurrence.actual_amount or Decimal("0")
        remaining = occurrence.expected_amount - actual
        return remaining if remaining > 0 else Decimal("0")
    return occurrence.expected_amount
