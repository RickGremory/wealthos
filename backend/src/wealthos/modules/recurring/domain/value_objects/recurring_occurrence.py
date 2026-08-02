"""Projected occurrence (calculated, not persisted as futures)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from wealthos.modules.recurring.domain.enums.occurrence import RecurringOccurrenceStatus
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringCertainty,
    RecurringDirection,
)
from wealthos.modules.recurring.domain.value_objects.occurrence_key import OccurrenceKey


@dataclass(frozen=True, slots=True)
class RecurringOccurrence:
    occurrence_key: OccurrenceKey
    recurring_rule_id: UUID
    organization_id: UUID
    original_expected_on: date
    expected_on: date
    expected_at: datetime
    direction: RecurringDirection
    base_amount: Decimal
    expected_amount: Decimal
    currency: str
    certainty: RecurringCertainty
    status: RecurringOccurrenceStatus
    category_id: UUID | None
    account_id: UUID | None
    destination_account_id: UUID | None
    is_exception: bool
    exception_id: UUID | None = None
    related_transaction_ids: tuple[UUID, ...] = ()
    actual_amount: Decimal | None = None
    variance_amount: Decimal | None = None
