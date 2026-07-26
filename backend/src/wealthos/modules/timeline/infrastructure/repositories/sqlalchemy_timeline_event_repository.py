"""SQLAlchemy implementation of TimelineEventRepository."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from wealthos.modules.timeline.domain.entities.timeline_event import TimelineEvent
from wealthos.modules.timeline.domain.repositories.timeline_event_repository import (
    TimelineCursor,
    TimelineListFilters,
)
from wealthos.modules.timeline.infrastructure.mappers.timeline_event_mapper import (
    TimelineEventMapper,
)
from wealthos.modules.timeline.infrastructure.models.timeline_event_model import (
    TimelineEventModel,
)
from wealthos.shared.base import BaseRepository

_IMPORTANCE_RANK = {
    "low": 0,
    "normal": 1,
    "high": 2,
    "critical": 3,
}


class SqlAlchemyTimelineEventRepository(BaseRepository[TimelineEventModel]):
    def __init__(
        self,
        session: Session,
        mapper: TimelineEventMapper | None = None,
    ) -> None:
        super().__init__(session, TimelineEventModel)
        self._mapper = mapper or TimelineEventMapper()

    def add(self, event: TimelineEvent) -> TimelineEvent:
        model = self._mapper.to_model(event)
        if model.created_at is None:
            model.created_at = datetime.now(UTC)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def add_idempotent(self, event: TimelineEvent) -> TimelineEvent | None:
        created_at = event.created_at or datetime.now(UTC)
        stmt = (
            insert(TimelineEventModel)
            .values(
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
                created_at=created_at,
            )
            .on_conflict_do_nothing(
                constraint="uq_timeline_events_idempotency",
            )
            .returning(TimelineEventModel.id)
        )
        row = self.session.execute(stmt).first()
        self.flush()
        if row is None:
            return None
        model = self.session.get(TimelineEventModel, row[0])
        assert model is not None
        return self._mapper.to_entity(model)

    def list_page(
        self,
        organization_id: UUID,
        *,
        filters: TimelineListFilters,
        limit: int,
        cursor: TimelineCursor | None = None,
    ) -> list[TimelineEvent]:
        stmt = select(TimelineEventModel).where(
            TimelineEventModel.organization_id == organization_id,
        )
        if filters.source_type:
            stmt = stmt.where(TimelineEventModel.source_type == filters.source_type)
        if filters.importance:
            stmt = stmt.where(TimelineEventModel.importance == filters.importance)
        if filters.min_importance:
            min_rank = _IMPORTANCE_RANK.get(filters.min_importance, 1)
            allowed = [k for k, v in _IMPORTANCE_RANK.items() if v >= min_rank]
            stmt = stmt.where(TimelineEventModel.importance.in_(allowed))
        if filters.currency:
            stmt = stmt.where(
                or_(
                    TimelineEventModel.currency == filters.currency,
                    TimelineEventModel.currency.is_(None),
                )
            )
        if filters.date_from is not None:
            stmt = stmt.where(TimelineEventModel.occurred_at >= filters.date_from)
        if filters.date_to is not None:
            stmt = stmt.where(TimelineEventModel.occurred_at <= filters.date_to)
        if cursor is not None:
            stmt = stmt.where(
                or_(
                    TimelineEventModel.occurred_at < cursor.occurred_at,
                    and_(
                        TimelineEventModel.occurred_at == cursor.occurred_at,
                        TimelineEventModel.id < cursor.id,
                    ),
                )
            )
        stmt = stmt.order_by(
            TimelineEventModel.occurred_at.desc(),
            TimelineEventModel.id.desc(),
        ).limit(limit)
        models = self.session.scalars(stmt).all()
        return [self._mapper.to_entity(m) for m in models]
