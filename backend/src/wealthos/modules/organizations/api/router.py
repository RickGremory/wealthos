"""HTTP routes for the organizations module."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from wealthos.modules.organizations.api.dependencies import get_create_organization_command
from wealthos.modules.organizations.application.commands.create_organization import (
    CreateOrganizationCommand,
    CreateOrganizationInput,
)
from wealthos.modules.organizations.domain.exceptions import (
    InvalidCurrency,
    InvalidLocale,
    InvalidTimezone,
    OrganizationError,
    OrganizationNameEmpty,
    OrganizationNameTooLong,
    OrganizationSlugAlreadyExists,
    OrganizationSlugInvalid,
)
from wealthos.modules.organizations.schemas.create import OrganizationCreate
from wealthos.modules.organizations.schemas.response import OrganizationRead

router = APIRouter()


@router.get("/health", include_in_schema=False)
async def organizations_module_health() -> dict[str, str]:
    """Scaffold probe for module registration."""
    return {"module": "organizations", "status": "ready"}


@router.post(
    "",
    response_model=OrganizationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization",
)
def create_organization(
    payload: OrganizationCreate,
    command: Annotated[
        CreateOrganizationCommand,
        Depends(get_create_organization_command),
    ],
) -> OrganizationRead:
    """Create a financial workspace (Organization)."""
    try:
        snapshot = command.execute(
            CreateOrganizationInput(
                name=payload.name,
                slug=payload.slug,
                currency=payload.currency,
                timezone=payload.timezone,
                locale=payload.locale,
            )
        )
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

    return OrganizationRead.from_snapshot(snapshot)
