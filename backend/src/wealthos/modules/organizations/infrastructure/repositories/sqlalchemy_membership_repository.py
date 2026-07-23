"""SQLAlchemy implementation of MembershipRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.identity.infrastructure.models.user_model import UserModel
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.organizations.domain.repositories.membership_repository import (
    OrganizationMemberView,
)
from wealthos.modules.organizations.infrastructure.mappers.membership_mapper import (
    MembershipMapper,
)
from wealthos.modules.organizations.infrastructure.models.organization_membership_model import (
    OrganizationMembershipModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyMembershipRepository(BaseRepository[OrganizationMembershipModel]):
    """Persist organization memberships through SQLAlchemy sessions."""

    def __init__(
        self,
        session: Session,
        mapper: MembershipMapper | None = None,
    ) -> None:
        super().__init__(session, OrganizationMembershipModel)
        self._mapper = mapper or MembershipMapper()

    def add(self, membership: OrganizationMembership) -> OrganizationMembership:
        model = self._mapper.to_model(membership)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_organization_and_user(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrganizationMembership | None:
        stmt = select(OrganizationMembershipModel).where(
            OrganizationMembershipModel.organization_id == organization_id,
            OrganizationMembershipModel.user_id == user_id,
        )
        model = self.session.scalars(stmt).first()
        if model is None:
            return None
        return self._mapper.to_entity(model)

    def list_by_organization(self, organization_id: UUID) -> list[OrganizationMemberView]:
        stmt = (
            select(
                OrganizationMembershipModel.id,
                OrganizationMembershipModel.user_id,
                UserModel.email,
                UserModel.display_name,
                OrganizationMembershipModel.role,
                OrganizationMembershipModel.status,
                OrganizationMembershipModel.created_at,
            )
            .join(UserModel, UserModel.id == OrganizationMembershipModel.user_id)
            .where(OrganizationMembershipModel.organization_id == organization_id)
            .order_by(OrganizationMembershipModel.created_at.asc())
        )
        rows = self.session.execute(stmt).all()
        return [
            OrganizationMemberView(
                membership_id=row.id,
                user_id=row.user_id,
                email=row.email,
                display_name=row.display_name,
                role=row.role,
                status=row.status,
                created_at=row.created_at,
            )
            for row in rows
        ]
