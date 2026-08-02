"""Pause window for a recurring series."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from wealthos.modules.recurring.domain.exceptions import InvalidPausePeriod


@dataclass
class RecurringRulePause:
    recurring_rule_id: UUID
    organization_id: UUID
    starts_on: date
    ends_on: date | None = None
    reason: str | None = None
    created_by: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.ends_on is not None and self.ends_on < self.starts_on:
            raise InvalidPausePeriod("Pause ends_on cannot precede starts_on.")

    @property
    def is_open(self) -> bool:
        return self.ends_on is None

    def contains(self, value: date) -> bool:
        if value < self.starts_on:
            return False
        if self.ends_on is None:
            return True
        return value <= self.ends_on

    def close_before(self, resume_on: date) -> None:
        """Close so ``resume_on`` is again eligible (ends_on = resume_on - 1 day)."""
        from datetime import timedelta

        if not self.is_open:
            raise InvalidPausePeriod("Pause is already closed.")
        ends = resume_on - timedelta(days=1)
        if ends < self.starts_on:
            raise InvalidPausePeriod("Resume date would empty the pause window.")
        self.ends_on = ends
        self.version += 1
