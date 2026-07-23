"""SQLAlchemy implementation of OrganizationRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.value_objects.slug import OrganizationSlug
from wealthos.modules.organizations.infrastructure.mappers.organization_mapper import (
    OrganizationMapper,
)
from wealthos.modules.organizations.infrastructure.models.organization_model import (
    OrganizationModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyOrganizationRepository(BaseRepository[OrganizationModel]):
    """Persist organizations through SQLAlchemy sessions."""

    def __init__(
        self,
        session: Session,
        mapper: OrganizationMapper | None = None,
    ) -> None:
        super().__init__(session, OrganizationModel)
        self._mapper = mapper or OrganizationMapper()

    def add(self, organization: Organization) -> Organization:
        model = self._mapper.to_model(organization)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(self, organization_id: UUID) -> Organization | None:
        stmt = select(OrganizationModel).where(
            OrganizationModel.id == organization_id,
            OrganizationModel.deleted_at.is_(None),
        )
        model = self.session.scalars(stmt).first()
        if model is None:
            return None
        return self._mapper.to_entity(model)

    def get_by_slug(self, slug: OrganizationSlug) -> Organization | None:
        stmt = select(OrganizationModel).where(
            OrganizationModel.slug == slug.value,
            OrganizationModel.deleted_at.is_(None),
        )
        model = self.session.scalars(stmt).first()
        if model is None:
            return None
        return self._mapper.to_entity(model)
