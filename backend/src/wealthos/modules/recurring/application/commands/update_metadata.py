"""Update non-structural notes on the current open version."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.recurring.application.commands._helpers import (
    ensure_expected_version,
    ensure_manual_writable,
    load_aggregate,
)
from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
)
from wealthos.modules.recurring.domain.exceptions import RecurringError
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringAggregateRepository,
)


@dataclass(frozen=True, slots=True)
class UpdateRecurringRuleMetadataCommand:
    organization_id: UUID
    actor_id: UUID
    rule_id: UUID
    expected_version: int
    notes: str | None = None


class UpdateRecurringRuleMetadataHandler:
    def __init__(self, repo: RecurringAggregateRepository) -> None:
        self._repo = repo

    def execute(
        self,
        command: UpdateRecurringRuleMetadataCommand,
    ) -> RecurringAggregate:
        aggregate = load_aggregate(
            self._repo,
            organization_id=command.organization_id,
            rule_id=command.rule_id,
            for_update=True,
        )
        ensure_manual_writable(aggregate)
        ensure_expected_version(aggregate, command.expected_version)

        current = next(
            (
                version
                for version in reversed(aggregate.versions_tuple())
                if version.effective_until is None
            ),
            None,
        )
        if current is None:
            raise RecurringError(
                "Rule has no open version.",
                code="recurring_rule_not_found",
            )
        current.notes = command.notes
        aggregate.rule.touch()
        return self._repo.save(aggregate, command.expected_version)
