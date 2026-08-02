"""Derive occurrence status from evaluation date and settlements."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Sequence

from wealthos.modules.recurring.domain.entities.occurrence_settlement import (
    RecurringOccurrenceSettlement,
)
from wealthos.modules.recurring.domain.enums.occurrence import (
    RecurringOccurrenceStatus,
    RecurringSettlementMode,
)


class OccurrenceStatusResolver:
    def resolve(
        self,
        *,
        expected_on: date,
        evaluated_on: date,
        grace_period_days: int,
        skipped: bool,
        cancelled: bool,
        expected_amount: Decimal,
        settlement_mode: RecurringSettlementMode,
        settlements: Sequence[RecurringOccurrenceSettlement],
    ) -> RecurringOccurrenceStatus:
        if skipped:
            return RecurringOccurrenceStatus.SKIPPED
        if cancelled:
            return RecurringOccurrenceStatus.CANCELLED

        active = [item for item in settlements if not item.is_voided]
        if settlement_mode is RecurringSettlementMode.SINGLE_TRANSACTION:
            if active:
                return RecurringOccurrenceStatus.SETTLED
        else:
            settled_amount = sum((item.settled_amount for item in active), Decimal("0"))
            if settled_amount >= expected_amount:
                return RecurringOccurrenceStatus.SETTLED
            if settled_amount > 0:
                return RecurringOccurrenceStatus.PARTIALLY_SETTLED

        grace_end = expected_on + timedelta(days=grace_period_days)
        if evaluated_on < expected_on:
            return RecurringOccurrenceStatus.UPCOMING
        if expected_on <= evaluated_on <= grace_end:
            return RecurringOccurrenceStatus.DUE
        return RecurringOccurrenceStatus.OVERDUE
