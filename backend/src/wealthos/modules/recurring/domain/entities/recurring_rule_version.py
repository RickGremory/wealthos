"""Temporal configuration version for a RecurringRule."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.recurring.domain.enums.occurrence import RecurringSettlementMode
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringAmountStrategy,
    RecurringCertainty,
    RecurringDirection,
)
from wealthos.modules.recurring.domain.exceptions import RecurringError
from wealthos.modules.recurring.domain.value_objects.effective_period import EffectivePeriod
from wealthos.modules.recurring.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)


@dataclass
class RecurringRuleVersion:
    recurring_rule_id: UUID
    organization_id: UUID
    effective_from: date
    name: str
    direction: RecurringDirection
    amount: Decimal
    currency: str
    pattern: RecurrencePattern
    starts_on: date
    amount_strategy: RecurringAmountStrategy = RecurringAmountStrategy.FIXED
    certainty: RecurringCertainty = RecurringCertainty.EXPECTED
    settlement_mode: RecurringSettlementMode = RecurringSettlementMode.SINGLE_TRANSACTION
    effective_until: date | None = None
    ends_on: date | None = None
    grace_period_days: int = 0
    account_id: UUID | None = None
    destination_account_id: UUID | None = None
    category_id: UUID | None = None
    notes: str | None = None
    created_by: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise RecurringError("amount must be greater than zero.", code="invalid_amount")
        if self.grace_period_days < 0:
            raise RecurringError(
                "grace_period_days must be >= 0.",
                code="invalid_grace_period",
            )
        if self.ends_on is not None and self.ends_on < self.starts_on:
            raise RecurringError(
                "ends_on cannot precede starts_on.",
                code="invalid_effective_date",
            )
        if (
            self.direction is RecurringDirection.TRANSFER
            and self.account_id is not None
            and self.destination_account_id is not None
            and self.account_id == self.destination_account_id
        ):
            raise RecurringError(
                "Transfer source and destination accounts must differ.",
                code="source_and_destination_must_differ",
            )
        # Validate effective period shape
        _ = self.effective_period

    @property
    def effective_period(self) -> EffectivePeriod:
        return EffectivePeriod(self.effective_from, self.effective_until)

    def close_on(self, until: date) -> None:
        if until < self.effective_from:
            raise RecurringError(
                "Cannot close version before effective_from.",
                code="invalid_effective_date",
            )
        self.effective_until = until
