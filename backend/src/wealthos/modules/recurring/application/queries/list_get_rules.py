"""List and get recurring rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from uuid import UUID

from wealthos.modules.recurring.application.dto.mappers import (
    occurrence_to_dto,
    schedule_label,
    version_to_dto,
)
from wealthos.modules.recurring.application.dto.views import (
    RecurringRuleDetailDTO,
    RecurringRuleListDTO,
)
from wealthos.modules.recurring.application.services.occurrence_expander import (
    RecurringOccurrenceExpander,
)
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringDirection,
    RecurringRuleStatus,
    RecurringSourceType,
)
from wealthos.modules.recurring.domain.exceptions import RecurringRuleNotFound
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringAggregateRepository,
    RecurringRuleFilters,
)


@dataclass(frozen=True, slots=True)
class ListRecurringRulesInput:
    organization_id: UUID
    evaluated_on: date
    timezone: str
    status: RecurringRuleStatus | None = None
    direction: RecurringDirection | None = None
    currency: str | None = None
    source_type: RecurringSourceType | None = None
    include_archived: bool = False


@dataclass(frozen=True, slots=True)
class GetRecurringRuleInput:
    organization_id: UUID
    rule_id: UUID
    evaluated_on: date
    timezone: str
    upcoming_days: int = 90


class ListRecurringRulesQuery:
    def __init__(
        self,
        repo: RecurringAggregateRepository,
        expander: RecurringOccurrenceExpander | None = None,
    ) -> None:
        self._repo = repo
        self._expander = expander or RecurringOccurrenceExpander()

    def execute(self, data: ListRecurringRulesInput) -> list[RecurringRuleListDTO]:
        filters = RecurringRuleFilters(
            status=data.status,
            direction=data.direction,
            currency=data.currency,
            source_type=data.source_type,
            include_archived=data.include_archived,
        )
        aggregates = self._repo.list_aggregates(data.organization_id, filters)
        horizon_end = data.evaluated_on + timedelta(days=30)
        results: list[RecurringRuleListDTO] = []
        for aggregate in aggregates:
            current = next(
                (
                    version
                    for version in reversed(aggregate.versions_tuple())
                    if version.effective_until is None
                ),
                aggregate.versions_tuple()[-1] if aggregate.versions else None,
            )
            if current is None:
                continue
            upcoming = self._expander.expand(
                aggregate,
                period_start=data.evaluated_on,
                period_end=horizon_end,
                evaluated_on=data.evaluated_on,
                timezone=data.timezone,
                currency=data.currency,
            )
            next_occ = None
            for item in upcoming:
                if item.status.value not in {"skipped", "cancelled", "settled"}:
                    next_occ = occurrence_to_dto(item, name=current.name)
                    break
            results.append(
                RecurringRuleListDTO(
                    id=aggregate.id,
                    name=current.name,
                    direction=current.direction.value,
                    amount=str(current.amount),
                    currency=current.currency,
                    status=aggregate.rule.status.value,
                    source_type=aggregate.rule.source_type.value,
                    is_managed_externally=aggregate.rule.is_managed_externally,
                    frequency=current.pattern.frequency.value,
                    interval=current.pattern.interval,
                    schedule_label=schedule_label(current),
                    version=aggregate.version,
                    next_occurrence=next_occ,
                )
            )
        return results


class GetRecurringRuleQuery:
    def __init__(
        self,
        repo: RecurringAggregateRepository,
        expander: RecurringOccurrenceExpander | None = None,
    ) -> None:
        self._repo = repo
        self._expander = expander or RecurringOccurrenceExpander()

    def execute(self, data: GetRecurringRuleInput) -> RecurringRuleDetailDTO:
        aggregate = self._repo.get(data.organization_id, data.rule_id)
        if aggregate is None:
            raise RecurringRuleNotFound("Recurring rule not found.")
        current = next(
            (
                version
                for version in reversed(aggregate.versions_tuple())
                if version.effective_until is None
            ),
            aggregate.versions_tuple()[-1] if aggregate.versions else None,
        )
        if current is None:
            raise RecurringRuleNotFound("Recurring rule has no versions.")
        upcoming = self._expander.expand(
            aggregate,
            period_start=data.evaluated_on,
            period_end=data.evaluated_on + timedelta(days=data.upcoming_days),
            evaluated_on=data.evaluated_on,
            timezone=data.timezone,
        )
        return RecurringRuleDetailDTO(
            id=aggregate.id,
            name=current.name,
            direction=current.direction.value,
            amount=str(current.amount),
            currency=current.currency,
            status=aggregate.rule.status.value,
            source_type=aggregate.rule.source_type.value,
            is_managed_externally=aggregate.rule.is_managed_externally,
            related_resource_type=aggregate.rule.related_resource_type,
            related_resource_id=aggregate.rule.related_resource_id,
            version=aggregate.version,
            created_at=aggregate.rule.created_at,
            updated_at=aggregate.rule.updated_at,
            archived_at=aggregate.rule.archived_at,
            current_version=version_to_dto(current),
            versions=tuple(version_to_dto(item) for item in aggregate.versions_tuple()),
            upcoming_occurrences=tuple(
                occurrence_to_dto(item, name=current.name) for item in upcoming
            ),
            notes=current.notes,
        )
