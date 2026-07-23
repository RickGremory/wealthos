"""Persistence port for Organization aggregates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.value_objects.slug import Slug


@dataclass(frozen=True, slots=True)
class OrganizationSnapshot:
    """Persistence-assigned state returned by the repository port.

    The domain entity has no technical id. After write/read through
    infrastructure, callers receive this snapshot for API and application use.
    """

    id: UUID
    name: str
    slug: str
    currency: str
    timezone: str
    locale: str
    created_at: datetime
    updated_at: datetime


class OrganizationRepository(Protocol):
    """Domain-facing repository. Implementations live in infrastructure."""

    def add(self, organization: Organization) -> OrganizationSnapshot:
        """Persist a new organization and return its stored snapshot."""
        ...

    def get_by_slug(self, slug: Slug) -> Organization | None:
        """Fetch aggregate by business slug, if present."""
        ...

    def list(self) -> list[Organization]:
        """Return all organizations visible in the current context."""
        ...
