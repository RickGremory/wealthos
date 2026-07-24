"""Organization access context for tenant-scoped endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.core.security.current_user import CurrentUser
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.organizations.infrastructure.repositories import (
    SqlAlchemyMembershipRepository,
    SqlAlchemyOrganizationRepository,
)


@dataclass(frozen=True, slots=True)
class OrganizationAccessContext:
    """Resolved membership plus organization settings needed by read models."""

    organization_id: UUID
    user_id: UUID
    role: str
    timezone: str
    currency: str
    membership: OrganizationMembership


def require_organization_access(
    organization_id: UUID,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_db)],
) -> OrganizationAccessContext:
    """Ensure active membership and load organization timezone/currency."""
    memberships = SqlAlchemyMembershipRepository(session)
    membership = memberships.get_by_organization_and_user(
        organization_id,
        current_user.id,
    )
    if membership is None or membership.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    organization = SqlAlchemyOrganizationRepository(session).get_by_id(organization_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    return OrganizationAccessContext(
        organization_id=organization_id,
        user_id=current_user.id,
        role=membership.role.value,
        timezone=organization.timezone.value,
        currency=organization.currency.value,
        membership=membership,
    )


OrganizationAccess = Annotated[
    OrganizationAccessContext,
    Depends(require_organization_access),
]
