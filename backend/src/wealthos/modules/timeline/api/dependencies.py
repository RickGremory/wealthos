"""FastAPI dependencies for timeline."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.accounts.infrastructure.repositories import (
    SqlAlchemyAccountRepository,
)
from wealthos.modules.timeline.application.projector import TimelineProjector
from wealthos.modules.timeline.application.publisher import EventPublisher
from wealthos.modules.timeline.application.queries.list_timeline import ListTimelineQuery
from wealthos.modules.timeline.domain.repositories.timeline_event_repository import (
    TimelineEventRepository,
)
from wealthos.modules.timeline.infrastructure.repositories import (
    SqlAlchemyTimelineEventRepository,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


def get_unit_of_work(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_timeline_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TimelineEventRepository:
    return SqlAlchemyTimelineEventRepository(session)


def get_account_repository(
    session: Annotated[Session, Depends(get_db)],
) -> AccountRepository:
    return SqlAlchemyAccountRepository(session)


def get_event_publisher(
    events: Annotated[TimelineEventRepository, Depends(get_timeline_repository)],
) -> EventPublisher:
    return EventPublisher(TimelineProjector(events))


def get_list_timeline_query(
    events: Annotated[TimelineEventRepository, Depends(get_timeline_repository)],
) -> ListTimelineQuery:
    return ListTimelineQuery(events)
