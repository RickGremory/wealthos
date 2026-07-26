"""Map TimelineEvent ↔ TimelineEventModel."""

from __future__ import annotations

from wealthos.modules.timeline.domain.entities.timeline_event import TimelineEvent
from wealthos.modules.timeline.infrastructure.models.timeline_event_model import (
    TimelineEventModel,
)


class TimelineEventMapper:
    def to_entity(self, model: TimelineEventModel) -> TimelineEvent:
        return TimelineEvent(
            id=model.id,
            organization_id=model.organization_id,
            occurred_at=model.occurred_at,
            source_type=model.source_type,
            event_type=model.event_type,
            importance=model.importance,
            title=model.title,
            description=model.description,
            resource_type=model.resource_type,
            resource_id=model.resource_id,
            currency=model.currency,
            amount=model.amount,
            metadata=dict(model.metadata_ or {}),
            created_at=model.created_at,
        )

    def to_model(self, event: TimelineEvent) -> TimelineEventModel:
        return TimelineEventModel(
            id=event.id,
            organization_id=event.organization_id,
            occurred_at=event.occurred_at,
            source_type=event.source_type,
            event_type=event.event_type,
            importance=event.importance,
            title=event.title,
            description=event.description,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            currency=event.currency,
            amount=event.amount,
            metadata_=dict(event.metadata or {}),
            created_at=event.created_at,
        )
