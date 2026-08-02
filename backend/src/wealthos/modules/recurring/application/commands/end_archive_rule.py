"""End and archive recurring rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from wealthos.modules.recurring.application.commands._helpers import (
    ensure_expected_version,
    ensure_manual_writable,
    load_aggregate,
)
from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
)
from wealthos.modules.recurring.domain.enums.rule import RecurringRuleStatus
from wealthos.modules.recurring.domain.exceptions import RecurringRuleManagedExternally
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringAggregateRepository,
)


@dataclass(frozen=True, slots=True)
class EndRecurringRuleCommand:
    organization_id: UUID
    actor_id: UUID
    rule_id: UUID
    ends_on: date
    expected_version: int
    today: date


@dataclass(frozen=True, slots=True)
class ArchiveRecurringRuleCommand:
    organization_id: UUID
    actor_id: UUID
    rule_id: UUID
    expected_version: int


class EndRecurringRuleHandler:
    def __init__(self, repo: RecurringAggregateRepository) -> None:
        self._repo = repo

    def execute(self, command: EndRecurringRuleCommand) -> RecurringAggregate:
        aggregate = load_aggregate(
            self._repo,
            organization_id=command.organization_id,
            rule_id=command.rule_id,
            for_update=True,
        )
        ensure_manual_writable(aggregate)
        ensure_expected_version(aggregate, command.expected_version)
        aggregate.end(command.ends_on, today=command.today)
        return self._repo.save(aggregate, command.expected_version)


class ArchiveRecurringRuleHandler:
    def __init__(self, repo: RecurringAggregateRepository) -> None:
        self._repo = repo

    def execute(self, command: ArchiveRecurringRuleCommand) -> RecurringAggregate:
        aggregate = load_aggregate(
            self._repo,
            organization_id=command.organization_id,
            rule_id=command.rule_id,
            for_update=True,
        )
        if aggregate.rule.is_managed_externally:
            raise RecurringRuleManagedExternally(
                "This recurring rule is managed by another module."
            )
        if aggregate.rule.status is RecurringRuleStatus.ARCHIVED:
            return aggregate
        ensure_expected_version(aggregate, command.expected_version)
        aggregate.archive()
        return self._repo.save(aggregate, command.expected_version)
