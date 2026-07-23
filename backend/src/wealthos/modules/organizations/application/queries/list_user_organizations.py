"""List organizations accessible by the current user."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.organizations.domain.repositories.membership_repository import (
    MembershipRepository,
    UserOrganizationView,
)


class ListUserOrganizationsQuery:
    """Read active organizations for a user via memberships JOIN."""

    def __init__(self, memberships: MembershipRepository) -> None:
        self._memberships = memberships

    def execute(self, user_id: UUID) -> list[UserOrganizationView]:
        return self._memberships.list_organizations_for_user(user_id)
