"""In-process FinancialEvent publisher (MVP bus)."""

from __future__ import annotations

from wealthos.modules.timeline.application.projector import TimelineProjector
from wealthos.modules.timeline.domain.entities.timeline_event import TimelineEvent
from wealthos.shared.events import FinancialEvent


class EventPublisher:
    """Sync in-process publisher. Same signature as a future async bus."""

    def __init__(self, projector: TimelineProjector) -> None:
        self._projector = projector

    def publish(self, event: FinancialEvent) -> TimelineEvent | None:
        return self._projector.project(event)

    def publish_many(self, events: list[FinancialEvent]) -> list[TimelineEvent]:
        projected: list[TimelineEvent] = []
        for event in events:
            row = self.publish(event)
            if row is not None:
                projected.append(row)
        return projected
