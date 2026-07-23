"""OrganizationMembership entity — access link between User and Organization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from wealthos.modules.organizations.domain.value_objects.membership_status import (
    MembershipStatus,
)
from wealthos.modules.organizations.domain.value_objects.organization_role import (
    OrganizationRole,
)


@dataclass(slots=True)
class OrganizationMembership:
    """Membership of a user in an organization."""

    id: UUID
    organization_id: UUID
    user_id: UUID
    role: OrganizationRole
    status: MembershipStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        user_id: UUID,
        role: str,
        membership_id: UUID | None = None,
        status: str = "active",
    ) -> OrganizationMembership:
        now = datetime.now(UTC)
        return cls(
            id=membership_id or uuid4(),
            organization_id=organization_id,
            user_id=user_id,
            role=OrganizationRole(role),
            status=MembershipStatus(status),
            created_at=now,
            updated_at=now,
        )
