"""SQLAlchemy BudgetAllocationRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.planning.domain.entities.budget_allocation import BudgetAllocation
from wealthos.modules.planning.infrastructure.mappers.budget_allocation_mapper import (
    BudgetAllocationMapper,
)
from wealthos.modules.planning.infrastructure.models.planning_models import (
    BudgetAllocationModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyBudgetAllocationRepository(BaseRepository[BudgetAllocationModel]):
    def __init__(
        self,
        session: Session,
        mapper: BudgetAllocationMapper | None = None,
    ) -> None:
        super().__init__(session, BudgetAllocationModel)
        self._mapper = mapper or BudgetAllocationMapper()

    def add(self, allocation: BudgetAllocation) -> BudgetAllocation:
        model = self._mapper.to_model(allocation)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(
        self,
        organization_id: UUID,
        allocation_id: UUID,
    ) -> BudgetAllocation | None:
        stmt = select(BudgetAllocationModel).where(
            BudgetAllocationModel.organization_id == organization_id,
            BudgetAllocationModel.id == allocation_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_by_budget(
        self,
        organization_id: UUID,
        budget_id: UUID,
    ) -> list[BudgetAllocation]:
        stmt = (
            select(BudgetAllocationModel)
            .where(
                BudgetAllocationModel.organization_id == organization_id,
                BudgetAllocationModel.budget_id == budget_id,
            )
            .order_by(BudgetAllocationModel.created_at.asc())
        )
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def save(self, allocation: BudgetAllocation) -> BudgetAllocation:
        model = self.session.get(BudgetAllocationModel, allocation.id)
        if model is None or model.organization_id != allocation.organization_id:
            raise LookupError("Budget allocation not found for save.")
        self._mapper.apply_to_model(allocation, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def remove(self, allocation: BudgetAllocation) -> None:
        model = self.session.get(BudgetAllocationModel, allocation.id)
        if model is None or model.organization_id != allocation.organization_id:
            raise LookupError("Budget allocation not found for remove.")
        self.delete(model)
        self.flush()
