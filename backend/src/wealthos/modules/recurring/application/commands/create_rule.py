"""CreateRecurringRule command."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
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
    RecurringSourceType,
)
from wealthos.modules.recurring.domain.exceptions import RecurringError
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
class CreateRecurringRuleCommand:
    organization_id: UUID
    actor_id: UUID
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
    source_type: RecurringSourceType = RecurringSourceType.MANUAL
    related_resource_type: str | None = None
    related_resource_id: UUID | None = None


class CreateRecurringRuleHandler:
    def __init__(
        self,
        repo: RecurringAggregateRepository,
        accounts: RecurringAccountValidationPort | None = None,
        categories: RecurringCategoryValidationPort | None = None,
    ) -> None:
        self._repo = repo
        self._accounts = accounts
        self._categories = categories

    def execute(self, command: CreateRecurringRuleCommand) -> RecurringAggregate:
        name = command.name.strip()
        if not name:
            raise RecurringError("name is required.", code="invalid_name")
        if command.amount <= 0:
            raise RecurringError("amount must be greater than zero.", code="invalid_amount")
        if command.direction is RecurringDirection.TRANSFER:
            if command.account_id is None or command.destination_account_id is None:
                raise RecurringError(
                    "Transfers require source and destination accounts.",
                    code="source_and_destination_must_differ",
                )
            if command.account_id == command.destination_account_id:
                raise RecurringError(
                    "Transfer source and destination accounts must differ.",
                    code="source_and_destination_must_differ",
                )

        if self._accounts is not None:
            self._accounts.validate_for_rule(
                command.organization_id,
                command.direction,
                command.account_id,
                command.destination_account_id,
                command.currency,
            )
        if command.category_id is not None and self._categories is not None:
            category = self._categories.get_category(
                command.organization_id,
                command.category_id,
            )
            if category is None or not category.is_active:
                raise RecurringError(
                    "Category not found.",
                    code="category_not_found",
                )

        rule = RecurringRule(
            organization_id=command.organization_id,
            source_type=command.source_type,
            related_resource_type=command.related_resource_type,
            related_resource_id=command.related_resource_id,
        )
        version = RecurringRuleVersion(
            recurring_rule_id=rule.id,
            organization_id=rule.organization_id,
            effective_from=command.starts_on,
            name=name,
            direction=command.direction,
            amount=command.amount,
            currency=command.currency.upper(),
            amount_strategy=command.amount_strategy,
            certainty=command.certainty,
            settlement_mode=command.settlement_mode,
            pattern=command.pattern,
            starts_on=command.starts_on,
            ends_on=command.ends_on,
            grace_period_days=command.grace_period_days,
            account_id=command.account_id,
            destination_account_id=command.destination_account_id,
            category_id=command.category_id,
            notes=command.notes,
            created_by=command.actor_id,
        )
        aggregate = RecurringAggregate(rule=rule, versions=[version])
        return self._repo.add(aggregate)
