"""Persistence port for timeline_events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from wealthos.modules.timeline.domain.entities.timeline_event import TimelineEvent


@dataclass(frozen=True, slots=True)
class TimelineListFilters:
    source_type: str | None = None
    importance: str | None = None
    currency: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    min_importance: str | None = None


@dataclass(frozen=True, slots=True)
class TimelineCursor:
    occurred_at: datetime
    id: UUID


class TimelineEventRepository(Protocol):
    def add(self, event: TimelineEvent) -> TimelineEvent: ...

    def add_idempotent(self, event: TimelineEvent) -> TimelineEvent | None:
        """Insert if unique key free; return None when duplicate."""
        ...

    def list_page(
        self,
        organization_id: UUID,
        *,
        filters: TimelineListFilters,
        limit: int,
        cursor: TimelineCursor | None = None,
    ) -> list[TimelineEvent]: ...
