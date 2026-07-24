"""SQLAlchemy TaxProfileRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.taxes.domain.entities.tax_profile import TaxProfile
from wealthos.modules.taxes.infrastructure.mappers.tax_profile_mapper import TaxProfileMapper
from wealthos.modules.taxes.infrastructure.models.tax_models import TaxProfileModel
from wealthos.shared.base import BaseRepository


class SqlAlchemyTaxProfileRepository(BaseRepository[TaxProfileModel]):
    def __init__(self, session: Session, mapper: TaxProfileMapper | None = None) -> None:
        super().__init__(session, TaxProfileModel)
        self._mapper = mapper or TaxProfileMapper()

    def add(self, profile: TaxProfile) -> TaxProfile:
        model = self._mapper.to_model(profile)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(self, organization_id: UUID, profile_id: UUID) -> TaxProfile | None:
        stmt = select(TaxProfileModel).where(
            TaxProfileModel.organization_id == organization_id,
            TaxProfileModel.id == profile_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def get_active(self, organization_id: UUID) -> TaxProfile | None:
        stmt = select(TaxProfileModel).where(
            TaxProfileModel.organization_id == organization_id,
            TaxProfileModel.is_active.is_(True),
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_by_organization(self, organization_id: UUID) -> list[TaxProfile]:
        stmt = (
            select(TaxProfileModel)
            .where(TaxProfileModel.organization_id == organization_id)
            .order_by(TaxProfileModel.created_at.desc())
        )
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def save(self, profile: TaxProfile) -> TaxProfile:
        model = self.session.get(TaxProfileModel, profile.id)
        if model is None or model.organization_id != profile.organization_id:
            raise LookupError("Tax profile not found for save.")
        self._mapper.apply_to_model(profile, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)
