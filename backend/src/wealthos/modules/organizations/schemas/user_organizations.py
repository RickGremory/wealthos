"""Schemas for /me/organizations."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from wealthos.modules.organizations.domain.repositories.membership_repository import (
    UserOrganizationView,
)


class UserOrganizationItem(BaseModel):
    id: UUID
    name: str
    slug: str
    currency: str
    timezone: str
    locale: str
    role: str

    @classmethod
    def from_view(cls, view: UserOrganizationView) -> UserOrganizationItem:
        return cls(
            id=view.id,
            name=view.name,
            slug=view.slug,
            currency=view.currency,
            timezone=view.timezone,
            locale=view.locale,
            role=view.role,
        )


class UserOrganizationListResponse(BaseModel):
    items: list[UserOrganizationItem]
    total: int
