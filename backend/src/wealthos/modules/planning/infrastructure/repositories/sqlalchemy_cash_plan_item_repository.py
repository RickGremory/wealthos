"""SQLAlchemy CashPlanItemRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.planning.domain.entities.cash_plan_item import CashPlanItem
from wealthos.modules.planning.infrastructure.mappers.cash_plan_item_mapper import (
    CashPlanItemMapper,
)
from wealthos.modules.planning.infrastructure.models.planning_models import (
    CashPlanItemModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyCashPlanItemRepository(BaseRepository[CashPlanItemModel]):
    def __init__(
        self,
        session: Session,
        mapper: CashPlanItemMapper | None = None,
    ) -> None:
        super().__init__(session, CashPlanItemModel)
        self._mapper = mapper or CashPlanItemMapper()

    def add(self, item: CashPlanItem) -> CashPlanItem:
        model = self._mapper.to_model(item)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(
        self,
        organization_id: UUID,
        item_id: UUID,
    ) -> CashPlanItem | None:
        stmt = select(CashPlanItemModel).where(
            CashPlanItemModel.organization_id == organization_id,
            CashPlanItemModel.id == item_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_by_plan(
        self,
        organization_id: UUID,
        cash_plan_id: UUID,
        *,
        include_cancelled: bool = True,
    ) -> list[CashPlanItem]:
        stmt = select(CashPlanItemModel).where(
            CashPlanItemModel.organization_id == organization_id,
            CashPlanItemModel.cash_plan_id == cash_plan_id,
        )
        if not include_cancelled:
            stmt = stmt.where(CashPlanItemModel.status != "cancelled")
        stmt = stmt.order_by(
            CashPlanItemModel.expected_date.asc(),
            CashPlanItemModel.created_at.asc(),
        )
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def save(self, item: CashPlanItem) -> CashPlanItem:
        model = self.session.get(CashPlanItemModel, item.id)
        if model is None or model.organization_id != item.organization_id:
            raise LookupError("Cash plan item not found for save.")
        self._mapper.apply_to_model(item, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def remove(self, item: CashPlanItem) -> None:
        model = self.session.get(CashPlanItemModel, item.id)
        if model is None or model.organization_id != item.organization_id:
            raise LookupError("Cash plan item not found for remove.")
        self.delete(model)
        self.flush()

    def lock_for_update(
        self,
        organization_id: UUID,
        item_id: UUID,
    ) -> CashPlanItem | None:
        return self.get_item_for_update(organization_id, item_id)

    def get_item_for_update(
        self,
        organization_id: UUID,
        item_id: UUID,
    ) -> CashPlanItem | None:
        stmt = (
            select(CashPlanItemModel)
            .where(
                CashPlanItemModel.organization_id == organization_id,
                CashPlanItemModel.id == item_id,
            )
            .with_for_update()
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None
