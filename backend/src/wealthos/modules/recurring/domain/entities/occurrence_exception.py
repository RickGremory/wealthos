"""Per-occurrence exception (skip / reschedule / amount / override)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.recurring.domain.enums.occurrence import RecurringExceptionType
from wealthos.modules.recurring.domain.enums.rule import RecurringCertainty
from wealthos.modules.recurring.domain.exceptions import InvalidOccurrenceException


@dataclass
class RecurringOccurrenceException:
    organization_id: UUID
    recurring_rule_id: UUID
    original_occurrence_key: str
    original_expected_on: date
    exception_type: RecurringExceptionType
    replacement_expected_on: date | None = None
    replacement_amount: Decimal | None = None
    replacement_certainty: RecurringCertainty | None = None
    reason: str | None = None
    is_active: bool = True
    created_by: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    deactivated_at: datetime | None = None

    def __post_init__(self) -> None:
        if (
            self.replacement_amount is not None
            and self.replacement_amount <= 0
        ):
            raise InvalidOccurrenceException("replacement_amount must be > 0.")
        if self.exception_type is RecurringExceptionType.SKIP:
            return
        if self.exception_type is RecurringExceptionType.RESCHEDULE:
            if self.replacement_expected_on is None:
                raise InvalidOccurrenceException(
                    "reschedule requires replacement_expected_on."
                )
            return
        if self.exception_type is RecurringExceptionType.AMOUNT_OVERRIDE:
            if self.replacement_amount is None:
                raise InvalidOccurrenceException(
                    "amount_override requires replacement_amount."
                )

    def deactivate(self, *, at: datetime | None = None) -> None:
        now = at or datetime.now(UTC)
        self.is_active = False
        self.deactivated_at = now
        self.updated_at = now
        self.version += 1
