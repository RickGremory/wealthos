"""Link between a projected occurrence and a ledger Transaction."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.recurring.domain.enums.occurrence import RecurringSettlementLinkType
from wealthos.modules.recurring.domain.exceptions import RecurringError


@dataclass
class RecurringOccurrenceSettlement:
    organization_id: UUID
    recurring_rule_id: UUID
    occurrence_key: str
    transaction_id: UUID
    settled_amount: Decimal
    link_type: RecurringSettlementLinkType
    linked_by: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    linked_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    voided_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.settled_amount <= 0:
            raise RecurringError(
                "settled_amount must be greater than zero.",
                code="invalid_amount",
            )

    @property
    def is_voided(self) -> bool:
        return self.voided_at is not None

    def void(self, *, at: datetime | None = None) -> None:
        if self.is_voided:
            return
        self.voided_at = at or datetime.now(UTC)
