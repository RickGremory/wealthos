"""Timeline API response schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from wealthos.modules.timeline.domain.entities.timeline_event import TimelineEvent


class TimelineEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    occurred_at: datetime
    source_type: str
    event_type: str
    importance: str
    title: str
    description: str
    resource_type: str
    resource_id: UUID
    currency: str | None = None
    amount: Decimal | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None

    @classmethod
    def from_entity(cls, event: TimelineEvent) -> TimelineEventResponse:
        return cls(
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
            metadata=dict(event.metadata or {}),
            created_at=event.created_at,
        )


class TimelineListResponse(BaseModel):
    items: list[TimelineEventResponse]
    next_cursor: str | None = None
    limit: int
