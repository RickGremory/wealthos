"""List timeline events with cursor pagination."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from wealthos.modules.timeline.domain.entities.timeline_event import TimelineEvent
from wealthos.modules.timeline.domain.repositories.timeline_event_repository import (
    TimelineCursor,
    TimelineEventRepository,
    TimelineListFilters,
)


@dataclass(frozen=True, slots=True)
class ListTimelineResult:
    items: list[TimelineEvent]
    next_cursor: str | None
    limit: int


def encode_cursor(occurred_at: datetime, event_id: UUID) -> str:
    payload = {"occurred_at": occurred_at.isoformat(), "id": str(event_id)}
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def decode_cursor(value: str) -> TimelineCursor:
    raw = base64.urlsafe_b64decode(value.encode("ascii"))
    payload = json.loads(raw.decode("utf-8"))
    return TimelineCursor(
        occurred_at=datetime.fromisoformat(payload["occurred_at"]),
        id=UUID(payload["id"]),
    )


class ListTimelineQuery:
    def __init__(self, events: TimelineEventRepository) -> None:
        self._events = events

    def execute(
        self,
        organization_id: UUID,
        *,
        limit: int = 40,
        cursor: str | None = None,
        source_type: str | None = None,
        importance: str | None = None,
        currency: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        min_importance: str | None = "normal",
    ) -> ListTimelineResult:
        limit = max(1, min(limit, 100))
        parsed = decode_cursor(cursor) if cursor else None
        filters = TimelineListFilters(
            source_type=source_type,
            importance=importance,
            currency=currency,
            date_from=date_from,
            date_to=date_to,
            min_importance=None if importance else min_importance,
        )
        # Fetch one extra to know if there is a next page.
        rows = self._events.list_page(
            organization_id,
            filters=filters,
            limit=limit + 1,
            cursor=parsed,
        )
        has_more = len(rows) > limit
        items = rows[:limit]
        next_cursor = None
        if has_more and items:
            last = items[-1]
            next_cursor = encode_cursor(last.occurred_at, last.id)
        return ListTimelineResult(items=items, next_cursor=next_cursor, limit=limit)
