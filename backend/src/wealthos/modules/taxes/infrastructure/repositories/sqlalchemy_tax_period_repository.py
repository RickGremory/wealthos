"""SQLAlchemy TaxPeriodRepository."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.taxes.domain.entities.tax_period import TaxPeriod
from wealthos.modules.taxes.infrastructure.mappers.tax_period_mapper import TaxPeriodMapper
from wealthos.modules.taxes.infrastructure.models.tax_models import TaxPeriodModel
from wealthos.shared.base import BaseRepository


class SqlAlchemyTaxPeriodRepository(BaseRepository[TaxPeriodModel]):
    def __init__(self, session: Session, mapper: TaxPeriodMapper | None = None) -> None:
        super().__init__(session, TaxPeriodModel)
        self._mapper = mapper or TaxPeriodMapper()

    def add(self, period: TaxPeriod) -> TaxPeriod:
        model = self._mapper.to_model(period)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(self, organization_id: UUID, period_id: UUID) -> TaxPeriod | None:
        stmt = select(TaxPeriodModel).where(
            TaxPeriodModel.organization_id == organization_id,
            TaxPeriodModel.id == period_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def get_by_range(
        self,
        tax_profile_id: UUID,
        date_from: date,
        date_to: date,
    ) -> TaxPeriod | None:
        stmt = select(TaxPeriodModel).where(
            TaxPeriodModel.tax_profile_id == tax_profile_id,
            TaxPeriodModel.date_from == date_from,
            TaxPeriodModel.date_to == date_to,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_by_profile(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
    ) -> list[TaxPeriod]:
        stmt = (
            select(TaxPeriodModel)
            .where(
                TaxPeriodModel.organization_id == organization_id,
                TaxPeriodModel.tax_profile_id == tax_profile_id,
            )
            .order_by(TaxPeriodModel.date_from.desc())
        )
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def lock_for_update(
        self,
        organization_id: UUID,
        period_id: UUID,
    ) -> TaxPeriod | None:
        stmt = (
            select(TaxPeriodModel)
            .where(
                TaxPeriodModel.organization_id == organization_id,
                TaxPeriodModel.id == period_id,
            )
            .with_for_update()
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def save(self, period: TaxPeriod) -> TaxPeriod:
        model = self.session.get(TaxPeriodModel, period.id)
        if model is None or model.organization_id != period.organization_id:
            raise LookupError("Tax period not found for save.")
        self._mapper.apply_to_model(period, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)
