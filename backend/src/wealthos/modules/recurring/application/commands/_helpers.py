"""Shared helpers for Recurring commands."""

from __future__ import annotations

from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
)
from wealthos.modules.recurring.domain.enums.rule import RecurringRuleStatus
from wealthos.modules.recurring.domain.exceptions import (
    RecurringConcurrentUpdate,
    RecurringRuleArchived,
    RecurringRuleEnded,
    RecurringRuleManagedExternally,
    RecurringRuleNotFound,
)
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringAggregateRepository,
)


def load_aggregate(
    repo: RecurringAggregateRepository,
    *,
    organization_id,
    rule_id,
    for_update: bool = False,
) -> RecurringAggregate:
    aggregate = repo.get(organization_id, rule_id, for_update=for_update)
    if aggregate is None:
        raise RecurringRuleNotFound("Recurring rule not found.")
    return aggregate


def ensure_manual_writable(aggregate: RecurringAggregate) -> None:
    if aggregate.rule.is_managed_externally:
        raise RecurringRuleManagedExternally(
            "This recurring rule is managed by another module."
        )
    if aggregate.rule.status is RecurringRuleStatus.ARCHIVED:
        raise RecurringRuleArchived("Archived rules cannot be modified.")
    if aggregate.rule.status is RecurringRuleStatus.ENDED:
        raise RecurringRuleEnded("Ended rules cannot be modified.")


def ensure_expected_version(aggregate: RecurringAggregate, expected_version: int) -> None:
    if aggregate.version != expected_version:
        raise RecurringConcurrentUpdate(
            "The recurring rule was modified by another request. Refresh and try again."
        )
