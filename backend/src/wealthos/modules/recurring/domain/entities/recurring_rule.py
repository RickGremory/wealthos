"""RecurringRule series shell (configuration lives on versions)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from wealthos.modules.recurring.domain.enums.rule import (
    RecurringRuleStatus,
    RecurringSourceType,
)


@dataclass
class RecurringRule:
    organization_id: UUID
    source_type: RecurringSourceType = RecurringSourceType.MANUAL
    status: RecurringRuleStatus = RecurringRuleStatus.ACTIVE
    related_resource_type: str | None = None
    related_resource_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    archived_at: datetime | None = None

    @property
    def is_managed_externally(self) -> bool:
        return self.source_type.is_managed_externally

    def touch(self, *, at: datetime | None = None) -> None:
        self.updated_at = at or datetime.now(UTC)
        self.version += 1

    def mark_archived(self, *, at: datetime | None = None) -> None:
        now = at or datetime.now(UTC)
        self.status = RecurringRuleStatus.ARCHIVED
        self.archived_at = now
        self.touch(at=now)

    def mark_ended(self, *, at: datetime | None = None) -> None:
        self.status = RecurringRuleStatus.ENDED
        self.touch(at=at)

    def mark_paused(self, *, at: datetime | None = None) -> None:
        self.status = RecurringRuleStatus.PAUSED
        self.touch(at=at)

    def mark_active(self, *, at: datetime | None = None) -> None:
        self.status = RecurringRuleStatus.ACTIVE
        self.touch(at=at)
