"""SQLAlchemy TaxCalculationRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from wealthos.modules.taxes.domain.entities.tax_calculation import TaxCalculation
from wealthos.modules.taxes.infrastructure.mappers.tax_calculation_mapper import (
    TaxCalculationMapper,
)
from wealthos.modules.taxes.infrastructure.models.tax_models import (
    TaxCalculationLineModel,
    TaxCalculationModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyTaxCalculationRepository(BaseRepository[TaxCalculationModel]):
    def __init__(
        self,
        session: Session,
        mapper: TaxCalculationMapper | None = None,
    ) -> None:
        super().__init__(session, TaxCalculationModel)
        self._mapper = mapper or TaxCalculationMapper()

    def add(self, calculation: TaxCalculation) -> TaxCalculation:
        model = self._mapper.to_model(calculation)
        super().add(model)
        self.flush()
        for line in calculation.lines:
            self.session.add(self._mapper.line_to_model(line))
        self.flush()
        self.refresh(model)
        return self._to_entity(model)

    def get_by_id(
        self,
        organization_id: UUID,
        calculation_id: UUID,
    ) -> TaxCalculation | None:
        stmt = select(TaxCalculationModel).where(
            TaxCalculationModel.organization_id == organization_id,
            TaxCalculationModel.id == calculation_id,
        )
        model = self.session.scalars(stmt).first()
        return self._to_entity(model) if model else None

    def get_latest_by_period(
        self,
        organization_id: UUID,
        tax_period_id: UUID,
    ) -> TaxCalculation | None:
        stmt = (
            select(TaxCalculationModel)
            .where(
                TaxCalculationModel.organization_id == organization_id,
                TaxCalculationModel.tax_period_id == tax_period_id,
                TaxCalculationModel.status == "completed",
            )
            .order_by(TaxCalculationModel.version.desc())
            .limit(1)
        )
        model = self.session.scalars(stmt).first()
        return self._to_entity(model) if model else None

    def get_next_version(self, tax_period_id: UUID) -> int:
        stmt = select(func.coalesce(func.max(TaxCalculationModel.version), 0)).where(
            TaxCalculationModel.tax_period_id == tax_period_id
        )
        current = self.session.scalar(stmt) or 0
        return int(current) + 1

    def supersede_completed(self, tax_period_id: UUID) -> None:
        self.session.execute(
            update(TaxCalculationModel)
            .where(
                TaxCalculationModel.tax_period_id == tax_period_id,
                TaxCalculationModel.status == "completed",
            )
            .values(status="superseded")
        )

    def _to_entity(self, model: TaxCalculationModel) -> TaxCalculation:
        lines_stmt = select(TaxCalculationLineModel).where(
            TaxCalculationLineModel.tax_calculation_id == model.id
        )
        lines = [
            self._mapper.line_to_entity(line_model)
            for line_model in self.session.scalars(lines_stmt)
        ]
        return self._mapper.to_entity(model, lines=lines)
