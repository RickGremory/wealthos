"""HTTP routes for the organizations module."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from wealthos.core.security.current_user import CurrentUser
from wealthos.core.security.organization_access import OrganizationMember
from wealthos.modules.identity.domain.exceptions import UserNotFoundError
from wealthos.modules.organizations.api.dependencies import (
    get_add_organization_member_command,
    get_create_organization_command,
    get_list_organization_members_query,
    get_membership_repository,
    get_unit_of_work,
)
from wealthos.modules.organizations.application.commands.add_organization_member import (
    AddOrganizationMemberCommand,
    AddOrganizationMemberInput,
)
from wealthos.modules.organizations.application.commands.create_organization import (
    CreateOrganizationCommand,
    CreateOrganizationInput,
)
from wealthos.modules.organizations.application.queries.list_organization_members import (
    ListOrganizationMembersQuery,
)
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.organizations.domain.exceptions import (
    InvalidCurrency,
    InvalidLocale,
    InvalidOrganizationRole,
    InvalidTimezone,
    OrganizationError,
    OrganizationMemberAlreadyExists,
    OrganizationNameEmpty,
    OrganizationNameTooLong,
    OrganizationNotFoundError,
    OrganizationSlugAlreadyExists,
    OrganizationSlugInvalid,
)
from wealthos.modules.organizations.domain.repositories.membership_repository import (
    MembershipRepository,
)
from wealthos.modules.organizations.schemas.create import OrganizationCreate
from wealthos.modules.organizations.schemas.membership import (
    AddOrganizationMemberRequest,
    OrganizationMemberItem,
    OrganizationMemberListResponse,
    OrganizationMembershipResponse,
)
from wealthos.modules.organizations.schemas.response import OrganizationResponse
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

router = APIRouter()


@router.get("/health", include_in_schema=False)
async def organizations_module_health() -> dict[str, str]:
    """Scaffold probe for module registration."""
    return {"module": "organizations", "status": "ready"}


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization",
)
def create_organization(
    payload: OrganizationCreate,
    current_user: CurrentUser,
    command: Annotated[CreateOrganizationCommand, Depends(get_create_organization_command)],
    memberships: Annotated[MembershipRepository, Depends(get_membership_repository)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> OrganizationResponse:
    """Create a financial workspace owned by the current user."""
    try:
        with uow:
            organization = command.execute(
                CreateOrganizationInput(
                    name=payload.name,
                    slug=payload.slug,
                    currency=payload.currency,
                    timezone=payload.timezone,
                    locale=payload.locale,
                )
            )
            memberships.add(
                OrganizationMembership.create(
                    organization_id=organization.id,
                    user_id=current_user.id,
                    role="owner",
                )
            )
            uow.commit()
    except OrganizationSlugAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (
        OrganizationNameEmpty,
        OrganizationNameTooLong,
        OrganizationSlugInvalid,
        InvalidCurrency,
        InvalidTimezone,
        InvalidLocale,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except OrganizationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return OrganizationResponse.from_entity(organization)


@router.post(
    "/{organization_id}/members",
    response_model=OrganizationMembershipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add organization member",
)
def add_organization_member(
    organization_id: UUID,
    payload: AddOrganizationMemberRequest,
    _membership: OrganizationMember,
    command: Annotated[
        AddOrganizationMemberCommand,
        Depends(get_add_organization_member_command),
    ],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> OrganizationMembershipResponse:
    try:
        with uow:
            membership = command.execute(
                AddOrganizationMemberInput(
                    organization_id=organization_id,
                    user_id=payload.user_id,
                    role=payload.role,
                )
            )
            uow.commit()
    except OrganizationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except OrganizationMemberAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InvalidOrganizationRole as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except OrganizationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return OrganizationMembershipResponse.from_entity(membership)


@router.get(
    "/{organization_id}/members",
    response_model=OrganizationMemberListResponse,
    summary="List organization members",
)
def list_organization_members(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[
        ListOrganizationMembersQuery,
        Depends(get_list_organization_members_query),
    ],
) -> OrganizationMemberListResponse:
    views = query.execute(organization_id)
    items = [OrganizationMemberItem.from_view(view) for view in views]
    return OrganizationMemberListResponse(items=items, total=len(items))
