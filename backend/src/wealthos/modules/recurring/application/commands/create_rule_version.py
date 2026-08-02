"""Create a new effective version (structural change from a date)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.recurring.application.commands._helpers import (
    ensure_expected_version,
    ensure_manual_writable,
    load_aggregate,
)
from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
)
from wealthos.modules.recurring.domain.entities.recurring_rule_version import (
    RecurringRuleVersion,
)
from wealthos.modules.recurring.domain.enums.occurrence import RecurringSettlementMode
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringAmountStrategy,
    RecurringCertainty,
    RecurringDirection,
)
from wealthos.modules.recurring.domain.exceptions import (
    RetroactiveStructuralChangeNotAllowed,
)
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringAggregateRepository,
)
from wealthos.modules.recurring.domain.ports.validation import (
    RecurringAccountValidationPort,
    RecurringCategoryValidationPort,
)
from wealthos.modules.recurring.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)


@dataclass(frozen=True, slots=True)
class RecurringVersionChanges:
    name: str
    direction: RecurringDirection
    amount: Decimal
    currency: str
    pattern: RecurrencePattern
    starts_on: date
    ends_on: date | None = None
    amount_strategy: RecurringAmountStrategy = RecurringAmountStrategy.FIXED
    certainty: RecurringCertainty = RecurringCertainty.EXPECTED
    settlement_mode: RecurringSettlementMode = RecurringSettlementMode.SINGLE_TRANSACTION
    account_id: UUID | None = None
    destination_account_id: UUID | None = None
    category_id: UUID | None = None
    grace_period_days: int = 0
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class CreateRecurringRuleVersionCommand:
    organization_id: UUID
    actor_id: UUID
    rule_id: UUID
    effective_from: date
    changes: RecurringVersionChanges
    expected_version: int
    today: date


class CreateRecurringRuleVersionHandler:
    def __init__(
        self,
        repo: RecurringAggregateRepository,
        accounts: RecurringAccountValidationPort | None = None,
        categories: RecurringCategoryValidationPort | None = None,
    ) -> None:
        self._repo = repo
        self._accounts = accounts
        self._categories = categories

    def execute(
        self,
        command: CreateRecurringRuleVersionCommand,
    ) -> RecurringAggregate:
        if command.effective_from < command.today:
            raise RetroactiveStructuralChangeNotAllowed(
                "Structural changes cannot start before today."
            )

        aggregate = load_aggregate(
            self._repo,
            organization_id=command.organization_id,
            rule_id=command.rule_id,
            for_update=True,
        )
        ensure_manual_writable(aggregate)
        ensure_expected_version(aggregate, command.expected_version)

        changes = command.changes
        if self._accounts is not None:
            self._accounts.validate_for_rule(
                command.organization_id,
                changes.direction,
                changes.account_id,
                changes.destination_account_id,
                changes.currency,
            )

        new_version = RecurringRuleVersion(
            recurring_rule_id=aggregate.id,
            organization_id=aggregate.organization_id,
            effective_from=command.effective_from,
            name=changes.name.strip(),
            direction=changes.direction,
            amount=changes.amount,
            currency=changes.currency.upper(),
            amount_strategy=changes.amount_strategy,
            certainty=changes.certainty,
            settlement_mode=changes.settlement_mode,
            pattern=changes.pattern,
            starts_on=changes.starts_on,
            ends_on=changes.ends_on,
            grace_period_days=changes.grace_period_days,
            account_id=changes.account_id,
            destination_account_id=changes.destination_account_id,
            category_id=changes.category_id,
            notes=changes.notes,
            created_by=command.actor_id,
        )
        aggregate.close_current_and_add_version(
            effective_from=command.effective_from,
            new_version=new_version,
        )
        return self._repo.save(aggregate, command.expected_version)
