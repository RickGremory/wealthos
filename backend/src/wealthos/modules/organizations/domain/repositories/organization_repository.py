"""Persistence port for Organization aggregates."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.value_objects.slug import OrganizationSlug


class OrganizationRepository(Protocol):
    """Domain-facing repository. Implementations live in infrastructure."""

    def add(self, organization: Organization) -> Organization:
        """Persist a new organization and return the stored aggregate."""
        ...

    def get_by_id(self, organization_id: UUID) -> Organization | None:
        """Fetch by technical/domain UUID identity."""
        ...

    def get_by_slug(self, slug: OrganizationSlug) -> Organization | None:
        """Fetch by business slug."""
        ...
