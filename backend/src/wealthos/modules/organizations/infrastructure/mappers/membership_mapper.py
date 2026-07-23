"""Map OrganizationMembership ↔ OrganizationMembershipModel."""

from __future__ import annotations

from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.organizations.domain.value_objects.membership_status import (
    MembershipStatus,
)
from wealthos.modules.organizations.domain.value_objects.organization_role import (
    OrganizationRole,
)
from wealthos.modules.organizations.infrastructure.models.organization_membership_model import (
    OrganizationMembershipModel,
)
from wealthos.shared.base import BaseMapper


class MembershipMapper(BaseMapper[OrganizationMembershipModel, OrganizationMembership]):
    """Convert between membership model and domain entity."""

    def to_entity(self, model: OrganizationMembershipModel) -> OrganizationMembership:
        return OrganizationMembership(
            id=model.id,
            organization_id=model.organization_id,
            user_id=model.user_id,
            role=OrganizationRole(model.role),
            status=MembershipStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: OrganizationMembership) -> OrganizationMembershipModel:
        return OrganizationMembershipModel(
            id=entity.id,
            organization_id=entity.organization_id,
            user_id=entity.user_id,
            role=entity.role.value,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
