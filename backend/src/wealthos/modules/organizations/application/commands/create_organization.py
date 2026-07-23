"""CreateOrganization command — write path for a new financial workspace."""

from __future__ import annotations

from dataclasses import dataclass

from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.exceptions import OrganizationSlugAlreadyExists
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationRepository,
    OrganizationSnapshot,
)
from wealthos.modules.organizations.domain.value_objects.slug import Slug


@dataclass(frozen=True, slots=True)
class CreateOrganizationInput:
    """Application input for creating an organization."""

    name: str
    slug: str
    currency: str = "MXN"
    timezone: str = "America/Mexico_City"
    locale: str = "es_MX"


class CreateOrganizationCommand:
    """Create an organization through the repository port."""

    def __init__(self, repository: OrganizationRepository) -> None:
        self._repository = repository

    def execute(self, data: CreateOrganizationInput) -> OrganizationSnapshot:
        organization = Organization.create(
            name=data.name,
            slug=data.slug,
            currency=data.currency,
            timezone=data.timezone,
            locale=data.locale,
        )

        if self._repository.get_by_slug(Slug(data.slug)) is not None:
            raise OrganizationSlugAlreadyExists(
                f"Organization slug '{data.slug}' is already taken."
            )

        return self._repository.add(organization)
