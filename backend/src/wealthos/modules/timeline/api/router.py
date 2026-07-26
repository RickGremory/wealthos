"""HTTP routes for Financial Timeline."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from wealthos.core.security.organization_access import OrganizationMember
from wealthos.modules.timeline.api.dependencies import get_list_timeline_query
from wealthos.modules.timeline.application.queries.list_timeline import ListTimelineQuery
from wealthos.modules.timeline.schemas.response import (
    TimelineEventResponse,
    TimelineListResponse,
)

router = APIRouter()

SourceTypeFilter = Literal["transaction", "goal", "commitment", "planning", "tax", "system"]
ImportanceFilter = Literal["low", "normal", "high", "critical"]


@router.get(
    "/{organization_id}/timeline",
    response_model=TimelineListResponse,
    summary="List financial timeline events",
)
def list_timeline(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListTimelineQuery, Depends(get_list_timeline_query)],
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 40,
    source_type: Annotated[SourceTypeFilter | None, Query()] = None,
    importance: Annotated[ImportanceFilter | None, Query()] = None,
    currency: Annotated[str | None, Query(min_length=3, max_length=3)] = None,
    date_from: Annotated[datetime | None, Query()] = None,
    date_to: Annotated[datetime | None, Query()] = None,
) -> TimelineListResponse:
    try:
        result = query.execute(
            organization_id,
            limit=limit,
            cursor=cursor,
            source_type=source_type,
            importance=importance,
            currency=currency.upper() if currency else None,
            date_from=date_from,
            date_to=date_to,
            min_importance="normal",
        )
    except (ValueError, KeyError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid cursor.",
        ) from exc
    return TimelineListResponse(
        items=[TimelineEventResponse.from_entity(item) for item in result.items],
        next_cursor=result.next_cursor,
        limit=result.limit,
    )
