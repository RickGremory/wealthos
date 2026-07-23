"""Persistence port for organization memberships."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)


@dataclass(frozen=True, slots=True)
class OrganizationMemberView:
    """Read projection for listing organization members."""

    membership_id: UUID
    user_id: UUID
    email: str
    display_name: str
    role: str
    status: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class UserOrganizationView:
    """Read projection for organizations accessible by a user."""

    id: UUID
    name: str
    slug: str
    currency: str
    timezone: str
    locale: str
    role: str


class MembershipRepository(Protocol):
    """Domain-facing membership repository."""

    def add(self, membership: OrganizationMembership) -> OrganizationMembership:
        """Persist a new membership."""
        ...

    def get_by_organization_and_user(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrganizationMembership | None:
        """Fetch membership for a user inside an organization."""
        ...

    def list_by_organization(self, organization_id: UUID) -> list[OrganizationMemberView]:
        """List members with user projection fields."""
        ...

    def list_organizations_for_user(self, user_id: UUID) -> list[UserOrganizationView]:
        """List active organizations for a user (memberships JOIN organizations)."""
        ...
