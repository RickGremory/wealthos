"""Preview and list recurring occurrences."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.recurring.application.dto.mappers import occurrence_to_dto
from wealthos.modules.recurring.application.dto.views import (
    RecurringOccurrenceDTO,
    RecurringPreviewDTO,
)
from wealthos.modules.recurring.application.services.occurrence_expander import (
    RecurringOccurrenceExpander,
)
from wealthos.modules.recurring.domain.entities.recurring_rule import RecurringRule
from wealthos.modules.recurring.domain.entities.recurring_rule_version import (
    RecurringRuleVersion,
)
from wealthos.modules.recurring.domain.enums.occurrence import RecurringSettlementMode
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringAmountStrategy,
    RecurringCertainty,
    RecurringDirection,
    RecurringRuleStatus,
)
from wealthos.modules.recurring.domain.exceptions import RecurringRuleNotFound
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringAggregateRepository,
    RecurringRuleFilters,
    RecurringSettlementRepository,
)
from wealthos.modules.recurring.domain.services.recurrence_generator import (
    DefaultRecurrenceGenerator,
)
from wealthos.modules.recurring.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)


@dataclass(frozen=True, slots=True)
class PreviewUnsavedRecurringRuleInput:
    organization_id: UUID
    period_start: date
    period_end: date
    evaluated_on: date
    timezone: str
    name: str
    direction: RecurringDirection
    amount: Decimal
    currency: str
    pattern: RecurrencePattern
    starts_on: date
    ends_on: date | None = None
    amount_strategy: RecurringAmountStrategy = RecurringAmountStrategy.FIXED
    certainty: RecurringCertainty = RecurringCertainty.EXPECTED
    grace_period_days: int = 0


@dataclass(frozen=True, slots=True)
class PreviewRecurringRuleInput:
    organization_id: UUID
    rule_id: UUID
    period_start: date
    period_end: date
    evaluated_on: date
    timezone: str


@dataclass(frozen=True, slots=True)
class ListRecurringOccurrencesInput:
    organization_id: UUID
    period_start: date
    period_end: date
    evaluated_on: date
    timezone: str
    currency: str | None = None
    rule_id: UUID | None = None
    statuses: tuple[str, ...] = ()


class PreviewUnsavedRecurringRuleQuery:
    def __init__(self, generator: DefaultRecurrenceGenerator | None = None) -> None:
        self._generator = generator or DefaultRecurrenceGenerator()

    def execute(self, data: PreviewUnsavedRecurringRuleInput) -> RecurringPreviewDTO:
        rule = RecurringRule(organization_id=data.organization_id, id=uuid4())
        version = RecurringRuleVersion(
            recurring_rule_id=rule.id,
            organization_id=data.organization_id,
            effective_from=data.starts_on,
            name=data.name,
            direction=data.direction,
            amount=data.amount,
            currency=data.currency.upper(),
            amount_strategy=data.amount_strategy,
            certainty=data.certainty,
            settlement_mode=RecurringSettlementMode.SINGLE_TRANSACTION,
            pattern=data.pattern,
            starts_on=data.starts_on,
            ends_on=data.ends_on,
            grace_period_days=data.grace_period_days,
        )
        occurrences = self._generator.generate(
            rule=rule,
            version=version,
            period_start=data.period_start,
            period_end=data.period_end,
            evaluated_on=data.evaluated_on,
            timezone=data.timezone,
        )
        return RecurringPreviewDTO(
            dates=tuple(item.expected_on for item in occurrences),
            occurrences=tuple(
                occurrence_to_dto(item, name=data.name) for item in occurrences
            ),
        )


class PreviewRecurringRuleQuery:
    def __init__(
        self,
        repo: RecurringAggregateRepository,
        settlements: RecurringSettlementRepository | None = None,
        expander: RecurringOccurrenceExpander | None = None,
    ) -> None:
        self._repo = repo
        self._settlements = settlements
        self._expander = expander or RecurringOccurrenceExpander()

    def execute(self, data: PreviewRecurringRuleInput) -> RecurringPreviewDTO:
        aggregate = self._repo.get(data.organization_id, data.rule_id)
        if aggregate is None:
            raise RecurringRuleNotFound("Recurring rule not found.")
        settlements = ()
        if self._settlements is not None:
            # Expand once without settlements to discover keys, then reload with links.
            draft = self._expander.expand(
                aggregate,
                period_start=data.period_start,
                period_end=data.period_end,
                evaluated_on=data.evaluated_on,
                timezone=data.timezone,
            )
            keys = tuple(item.occurrence_key.value for item in draft)
            settlements = tuple(
                self._settlements.list_for_keys(data.organization_id, keys)
            )
        occurrences = self._expander.expand(
            aggregate,
            period_start=data.period_start,
            period_end=data.period_end,
            evaluated_on=data.evaluated_on,
            timezone=data.timezone,
            settlements=settlements,
        )
        current = aggregate.current_version(data.evaluated_on) or (
            aggregate.versions_tuple()[-1] if aggregate.versions else None
        )
        name = current.name if current else "Recurring"
        return RecurringPreviewDTO(
            dates=tuple(item.expected_on for item in occurrences),
            occurrences=tuple(
                occurrence_to_dto(item, name=name) for item in occurrences
            ),
        )


class ListRecurringOccurrencesQuery:
    def __init__(
        self,
        repo: RecurringAggregateRepository,
        settlements: RecurringSettlementRepository | None = None,
        expander: RecurringOccurrenceExpander | None = None,
    ) -> None:
        self._repo = repo
        self._settlements = settlements
        self._expander = expander or RecurringOccurrenceExpander()

    def execute(
        self,
        data: ListRecurringOccurrencesInput,
    ) -> list[RecurringOccurrenceDTO]:
        if data.rule_id is not None:
            aggregates = []
            aggregate = self._repo.get(data.organization_id, data.rule_id)
            if aggregate is None:
                raise RecurringRuleNotFound("Recurring rule not found.")
            aggregates = [aggregate]
        else:
            aggregates = self._repo.list_aggregates(
                data.organization_id,
                RecurringRuleFilters(
                    include_archived=False,
                    currency=data.currency,
                ),
            )
            # Also skip ended/archived already filtered; include paused (pauses apply)
            aggregates = [
                item
                for item in aggregates
                if item.rule.status
                not in {RecurringRuleStatus.ARCHIVED, RecurringRuleStatus.ENDED}
            ]

        results: list[RecurringOccurrenceDTO] = []
        for aggregate in aggregates:
            settlements = ()
            occurrences = self._expander.expand(
                aggregate,
                period_start=data.period_start,
                period_end=data.period_end,
                evaluated_on=data.evaluated_on,
                timezone=data.timezone,
                currency=data.currency,
            )
            if self._settlements is not None and occurrences:
                keys = tuple(item.occurrence_key.value for item in occurrences)
                settlements = tuple(
                    self._settlements.list_for_keys(data.organization_id, keys)
                )
                occurrences = self._expander.expand(
                    aggregate,
                    period_start=data.period_start,
                    period_end=data.period_end,
                    evaluated_on=data.evaluated_on,
                    timezone=data.timezone,
                    currency=data.currency,
                    settlements=settlements,
                )
            current = aggregate.current_version(data.evaluated_on) or (
                aggregate.versions_tuple()[-1] if aggregate.versions else None
            )
            name = current.name if current else "Recurring"
            exception_types = {
                item.original_occurrence_key: item.exception_type.value
                for item in aggregate.active_exceptions()
            }
            for occurrence in occurrences:
                if data.statuses and occurrence.status.value not in data.statuses:
                    continue
                results.append(
                    occurrence_to_dto(
                        occurrence,
                        name=name,
                        exception_type=exception_types.get(
                            occurrence.occurrence_key.value
                        ),
                    )
                )
        results.sort(key=lambda item: (item.expected_on, item.occurrence_key))
        return results
