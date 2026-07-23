"""Response schema for organization resources."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from wealthos.modules.organizations.domain.entities.organization import Organization


class OrganizationResponse(BaseModel):
    """Public organization representation for OpenAPI responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    currency: str
    timezone: str
    locale: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, organization: Organization) -> OrganizationResponse:
        return cls(
            id=organization.id,
            name=organization.name.value,
            slug=organization.slug.value,
            currency=organization.currency.value,
            timezone=organization.timezone.value,
            locale=organization.locale.value,
            created_at=organization.created_at,
            updated_at=organization.updated_at,
        )
