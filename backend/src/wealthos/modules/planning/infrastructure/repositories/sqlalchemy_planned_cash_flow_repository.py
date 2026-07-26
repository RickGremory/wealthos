"""SQLAlchemy PlannedCashFlowRepository."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.planning.domain.entities.planned_cash_flow import PlannedCashFlow
from wealthos.modules.planning.infrastructure.mappers.planned_cash_flow_mapper import (
    PlannedCashFlowMapper,
)
from wealthos.modules.planning.infrastructure.models.planning_projection_models import (
    PlannedCashFlowModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyPlannedCashFlowRepository(BaseRepository[PlannedCashFlowModel]):
    def __init__(
        self,
        session: Session,
        mapper: PlannedCashFlowMapper | None = None,
    ) -> None:
        super().__init__(session, PlannedCashFlowModel)
        self._mapper = mapper or PlannedCashFlowMapper()

    def add(self, cash_flow: PlannedCashFlow) -> PlannedCashFlow:
        model = self._mapper.to_model(cash_flow)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(
        self,
        organization_id: UUID,
        cash_flow_id: UUID,
    ) -> PlannedCashFlow | None:
        stmt = select(PlannedCashFlowModel).where(
            PlannedCashFlowModel.organization_id == organization_id,
            PlannedCashFlowModel.id == cash_flow_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        currency: str | None = None,
        status: str | None = None,
        direction: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> list[PlannedCashFlow]:
        stmt = select(PlannedCashFlowModel).where(
            PlannedCashFlowModel.organization_id == organization_id
        )
        if currency is not None:
            stmt = stmt.where(PlannedCashFlowModel.currency == currency.strip().upper())
        if status is not None:
            stmt = stmt.where(PlannedCashFlowModel.status == status)
        if direction is not None:
            stmt = stmt.where(PlannedCashFlowModel.direction == direction)
        if date_from is not None:
            stmt = stmt.where(PlannedCashFlowModel.expected_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(PlannedCashFlowModel.expected_at <= date_to)
        stmt = (
            stmt.order_by(
                PlannedCashFlowModel.expected_at.asc(),
                PlannedCashFlowModel.created_at.asc(),
            )
            .limit(limit)
            .offset(offset)
        )
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def list_active_in_period(
        self,
        organization_id: UUID,
        *,
        currency: str,
        period_start: datetime,
        period_end: datetime,
    ) -> list[PlannedCashFlow]:
        return self.list_by_organization(
            organization_id,
            currency=currency,
            status="active",
            date_from=period_start,
            date_to=period_end,
            limit=1000,
        )

    def save(self, cash_flow: PlannedCashFlow) -> PlannedCashFlow:
        model = self.session.get(PlannedCashFlowModel, cash_flow.id)
        if model is None or model.organization_id != cash_flow.organization_id:
            raise LookupError("Planned cash flow not found for save.")
        self._mapper.apply_to_model(cash_flow, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)
