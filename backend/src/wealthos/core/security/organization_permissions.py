"""Organization role authorization helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.core.security.current_user import CurrentUser
from wealthos.core.security.organization_access import require_organization_member
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)


def require_organization_role(
    *allowed_roles: str,
) -> Callable[..., OrganizationMembership]:
    """Factory: require an active membership with one of the given roles."""

    normalized = frozenset(role.strip().lower() for role in allowed_roles)

    def dependency(
        organization_id: UUID,
        current_user: CurrentUser,
        session: Annotated[Session, Depends(get_db)],
    ) -> OrganizationMembership:
        membership = require_organization_member(
            organization_id=organization_id,
            current_user=current_user,
            session=session,
        )
        if membership.role.value not in normalized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient organization role for this action.",
            )
        return membership

    return dependency
