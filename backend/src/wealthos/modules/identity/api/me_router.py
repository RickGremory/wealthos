"""Current-user resource routes (/api/v1/me)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.core.security.current_user import CurrentUser
from wealthos.modules.organizations.application.queries.list_user_organizations import (
    ListUserOrganizationsQuery,
)
from wealthos.modules.organizations.infrastructure.repositories import (
    SqlAlchemyMembershipRepository,
)
from wealthos.modules.organizations.schemas.user_organizations import (
    UserOrganizationItem,
    UserOrganizationListResponse,
)

router = APIRouter()


def get_list_user_organizations_query(
    session: Annotated[Session, Depends(get_db)],
) -> ListUserOrganizationsQuery:
    return ListUserOrganizationsQuery(SqlAlchemyMembershipRepository(session))


@router.get(
    "/organizations",
    response_model=UserOrganizationListResponse,
    summary="List organizations for the current user",
)
def list_my_organizations(
    current_user: CurrentUser,
    query: Annotated[
        ListUserOrganizationsQuery,
        Depends(get_list_user_organizations_query),
    ],
) -> UserOrganizationListResponse:
    views = query.execute(current_user.id)
    items = [UserOrganizationItem.from_view(view) for view in views]
    return UserOrganizationListResponse(items=items, total=len(items))
