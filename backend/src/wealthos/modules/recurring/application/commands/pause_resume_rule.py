"""Pause / resume recurring series."""

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
from wealthos.modules.recurring.domain.entities.recurring_rule_pause import (
    RecurringRulePause,
)
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringAggregateRepository,
)


@dataclass(frozen=True, slots=True)
class PauseRecurringRuleCommand:
    organization_id: UUID
    actor_id: UUID
    rule_id: UUID
    starts_on: date
    ends_on: date | None
    expected_version: int
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class ResumeRecurringRuleCommand:
    organization_id: UUID
    actor_id: UUID
    rule_id: UUID
    resume_on: date
    expected_version: int


class PauseRecurringRuleHandler:
    def __init__(self, repo: RecurringAggregateRepository) -> None:
        self._repo = repo

    def execute(self, command: PauseRecurringRuleCommand) -> RecurringAggregate:
        aggregate = load_aggregate(
            self._repo,
            organization_id=command.organization_id,
            rule_id=command.rule_id,
            for_update=True,
        )
        ensure_manual_writable(aggregate)
        ensure_expected_version(aggregate, command.expected_version)
        aggregate.add_pause(
            RecurringRulePause(
                recurring_rule_id=aggregate.id,
                organization_id=aggregate.organization_id,
                starts_on=command.starts_on,
                ends_on=command.ends_on,
                reason=command.reason,
                created_by=command.actor_id,
            )
        )
        return self._repo.save(aggregate, command.expected_version)


class ResumeRecurringRuleHandler:
    def __init__(self, repo: RecurringAggregateRepository) -> None:
        self._repo = repo

    def execute(self, command: ResumeRecurringRuleCommand) -> RecurringAggregate:
        aggregate = load_aggregate(
            self._repo,
            organization_id=command.organization_id,
            rule_id=command.rule_id,
            for_update=True,
        )
        ensure_manual_writable(aggregate)
        ensure_expected_version(aggregate, command.expected_version)
        aggregate.resume(command.resume_on)
        return self._repo.save(aggregate, command.expected_version)
