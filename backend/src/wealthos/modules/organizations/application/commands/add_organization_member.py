"""AddOrganizationMember command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.identity.domain.exceptions import UserNotFoundError
from wealthos.modules.identity.domain.repositories.user_repository import UserRepository
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.organizations.domain.exceptions import (
    OrganizationMemberAlreadyExists,
    OrganizationNotFoundError,
)
from wealthos.modules.organizations.domain.repositories.membership_repository import (
    MembershipRepository,
)
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationRepository,
)


@dataclass(frozen=True, slots=True)
class AddOrganizationMemberInput:
    organization_id: UUID
    user_id: UUID
    role: str


class AddOrganizationMemberCommand:
    """Attach a user to an organization with a role."""

    def __init__(
        self,
        *,
        organizations: OrganizationRepository,
        users: UserRepository,
        memberships: MembershipRepository,
    ) -> None:
        self._organizations = organizations
        self._users = users
        self._memberships = memberships

    def execute(self, data: AddOrganizationMemberInput) -> OrganizationMembership:
        if self._organizations.get_by_id(data.organization_id) is None:
            raise OrganizationNotFoundError(f"Organization '{data.organization_id}' was not found.")

        if self._users.get_by_id(data.user_id) is None:
            raise UserNotFoundError(f"User '{data.user_id}' was not found.")

        existing = self._memberships.get_by_organization_and_user(
            data.organization_id,
            data.user_id,
        )
        if existing is not None:
            raise OrganizationMemberAlreadyExists("User is already a member of this organization.")

        membership = OrganizationMembership.create(
            organization_id=data.organization_id,
            user_id=data.user_id,
            role=data.role,
        )
        return self._memberships.add(membership)
