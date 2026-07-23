"""Schemas for organization membership endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.organizations.domain.repositories.membership_repository import (
    OrganizationMemberView,
)


class AddOrganizationMemberRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    role: str = Field(default="member", min_length=1, max_length=20)


class OrganizationMembershipResponse(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    role: str
    status: str
    created_at: datetime

    @classmethod
    def from_entity(
        cls,
        membership: OrganizationMembership,
    ) -> OrganizationMembershipResponse:
        return cls(
            id=membership.id,
            organization_id=membership.organization_id,
            user_id=membership.user_id,
            role=membership.role.value,
            status=membership.status.value,
            created_at=membership.created_at,
        )


class OrganizationMemberItem(BaseModel):
    membership_id: UUID
    user_id: UUID
    email: str
    display_name: str
    role: str
    status: str

    @classmethod
    def from_view(cls, view: OrganizationMemberView) -> OrganizationMemberItem:
        return cls(
            membership_id=view.membership_id,
            user_id=view.user_id,
            email=view.email,
            display_name=view.display_name,
            role=view.role,
            status=view.status,
        )


class OrganizationMemberListResponse(BaseModel):
    items: list[OrganizationMemberItem]
    total: int
