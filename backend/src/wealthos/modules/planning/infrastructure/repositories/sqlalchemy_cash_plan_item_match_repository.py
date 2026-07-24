"""SQLAlchemy CashPlanItemMatchRepository."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from wealthos.modules.planning.domain.entities.cash_plan_item_match import CashPlanItemMatch
from wealthos.modules.planning.infrastructure.mappers.cash_plan_item_match_mapper import (
    CashPlanItemMatchMapper,
)
from wealthos.modules.planning.infrastructure.models.planning_models import (
    CashPlanItemMatchModel,
    CashPlanItemModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyCashPlanItemMatchRepository(BaseRepository[CashPlanItemMatchModel]):
    def __init__(
        self,
        session: Session,
        mapper: CashPlanItemMatchMapper | None = None,
    ) -> None:
        super().__init__(session, CashPlanItemMatchModel)
        self._mapper = mapper or CashPlanItemMatchMapper()

    def add(self, match: CashPlanItemMatch) -> CashPlanItemMatch:
        model = self._mapper.to_model(match)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def list_by_item(
        self,
        organization_id: UUID,
        cash_plan_item_id: UUID,
    ) -> list[CashPlanItemMatch]:
        stmt = (
            select(CashPlanItemMatchModel)
            .where(
                CashPlanItemMatchModel.organization_id == organization_id,
                CashPlanItemMatchModel.cash_plan_item_id == cash_plan_item_id,
            )
            .order_by(CashPlanItemMatchModel.created_at.asc())
        )
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def list_by_plan(
        self,
        organization_id: UUID,
        cash_plan_id: UUID,
    ) -> list[CashPlanItemMatch]:
        stmt = (
            select(CashPlanItemMatchModel)
            .join(
                CashPlanItemModel,
                CashPlanItemModel.id == CashPlanItemMatchModel.cash_plan_item_id,
            )
            .where(
                CashPlanItemMatchModel.organization_id == organization_id,
                CashPlanItemModel.cash_plan_id == cash_plan_id,
            )
            .order_by(CashPlanItemMatchModel.created_at.asc())
        )
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def sum_matched_amount(
        self,
        organization_id: UUID,
        cash_plan_item_id: UUID,
    ) -> Decimal:
        stmt = select(func.coalesce(func.sum(CashPlanItemMatchModel.matched_amount), 0)).where(
            CashPlanItemMatchModel.organization_id == organization_id,
            CashPlanItemMatchModel.cash_plan_item_id == cash_plan_item_id,
        )
        return Decimal(str(self.session.scalar(stmt) or 0))

    def remove(self, match: CashPlanItemMatch) -> None:
        model = self.session.get(CashPlanItemMatchModel, match.id)
        if model is None or model.organization_id != match.organization_id:
            raise LookupError("Cash plan item match not found for remove.")
        self.delete(model)
        self.flush()
