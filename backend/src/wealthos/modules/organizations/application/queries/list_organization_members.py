"""ListOrganizationMembers query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.organizations.domain.exceptions import OrganizationNotFoundError
from wealthos.modules.organizations.domain.repositories.membership_repository import (
    MembershipRepository,
    OrganizationMemberView,
)
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationRepository,
)


class ListOrganizationMembersQuery:
    """Read members of an organization with user projection fields."""

    def __init__(
        self,
        *,
        organizations: OrganizationRepository,
        memberships: MembershipRepository,
    ) -> None:
        self._organizations = organizations
        self._memberships = memberships

    def execute(self, organization_id: UUID) -> list[OrganizationMemberView]:
        if self._organizations.get_by_id(organization_id) is None:
            raise OrganizationNotFoundError(f"Organization '{organization_id}' was not found.")
        return self._memberships.list_by_organization(organization_id)
