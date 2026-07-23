"""Response schema for organization resources."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationSnapshot,
)


class OrganizationRead(BaseModel):
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
    def from_snapshot(cls, snapshot: OrganizationSnapshot) -> OrganizationRead:
        return cls(
            id=snapshot.id,
            name=snapshot.name,
            slug=snapshot.slug,
            currency=snapshot.currency,
            timezone=snapshot.timezone,
            locale=snapshot.locale,
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
        )
