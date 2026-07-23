"""Organization membership access dependency."""

from __future__ import annotations

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
)


def require_organization_member(
    organization_id: UUID,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_db)],
) -> OrganizationMembership:
    """Ensure the current user has an active membership in the organization.

    Missing organization or missing access both return 404 to avoid leaking
    private organization existence.
    """
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
    return membership


OrganizationMember = Annotated[
    OrganizationMembership,
    Depends(require_organization_member),
]
