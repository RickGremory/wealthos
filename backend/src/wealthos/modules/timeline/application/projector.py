"""Project FinancialEvent into timeline_events."""

from __future__ import annotations

from datetime import UTC, datetime

from wealthos.modules.timeline.domain.entities.timeline_event import TimelineEvent
from wealthos.modules.timeline.domain.repositories.timeline_event_repository import (
    TimelineEventRepository,
)
from wealthos.shared.events import FinancialEvent


class TimelineProjector:
    """Maps FinancialEvent → persisted TimelineEvent (skips importance=low)."""

    def __init__(self, events: TimelineEventRepository) -> None:
        self._events = events

    def project(self, event: FinancialEvent) -> TimelineEvent | None:
        if event.importance == "low":
            return None
        row = TimelineEvent(
            id=event.id,
            organization_id=event.organization_id,
            occurred_at=event.occurred_at,
            source_type=event.source_type,
            event_type=event.event_type,
            importance=event.importance,
            title=event.title[:200],
            description=event.description[:500],
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            currency=event.currency,
            amount=event.amount,
            metadata=dict(event.metadata or {}),
            created_at=datetime.now(UTC),
        )
        return self._events.add_idempotent(row)
