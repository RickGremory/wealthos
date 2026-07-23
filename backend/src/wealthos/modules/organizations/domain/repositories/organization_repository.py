"""Persistence port for Organization aggregates."""

from __future__ import annotations

from typing import Protocol

from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.value_objects.slug import Slug


class OrganizationRepository(Protocol):
    """Domain-facing repository. Implementations live in infrastructure."""

    def add(self, organization: Organization) -> Organization:
        """Persist a new organization and return the stored aggregate."""
        ...

    def get_by_slug(self, slug: Slug) -> Organization | None:
        """Fetch by business slug (domain identity before technical ids)."""
        ...

    def list(self) -> list[Organization]:
        """Return all organizations visible in the current context."""
        ...
