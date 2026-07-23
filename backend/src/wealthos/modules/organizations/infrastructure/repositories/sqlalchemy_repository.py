"""SQLAlchemy implementation of OrganizationRepository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationSnapshot,
)
from wealthos.modules.organizations.domain.value_objects.slug import Slug
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

    def add(self, organization: Organization) -> OrganizationSnapshot:
        model = self._mapper.to_model(organization)
        super().add(model)
        self.commit()
        self.refresh(model)
        return self._mapper.to_snapshot(model)

    def get_by_slug(self, slug: Slug) -> Organization | None:
        stmt = select(OrganizationModel).where(OrganizationModel.slug == slug.value)
        model = self.session.scalars(stmt).first()
        if model is None:
            return None
        return self._mapper.to_entity(model)

    def list(self) -> list[Organization]:
        stmt = select(OrganizationModel).order_by(OrganizationModel.created_at.asc())
        models = self.session.scalars(stmt).all()
        return [self._mapper.to_entity(model) for model in models]
