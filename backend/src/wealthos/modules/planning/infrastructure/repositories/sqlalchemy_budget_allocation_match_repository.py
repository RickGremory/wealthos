"""SQLAlchemy BudgetAllocationMatchRepository."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from wealthos.modules.planning.domain.entities.budget_allocation_match import (
    BudgetAllocationMatch,
)
from wealthos.modules.planning.infrastructure.mappers.budget_allocation_match_mapper import (
    BudgetAllocationMatchMapper,
)
from wealthos.modules.planning.infrastructure.models.planning_models import (
    BudgetAllocationMatchModel,
    BudgetAllocationModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyBudgetAllocationMatchRepository(BaseRepository[BudgetAllocationMatchModel]):
    def __init__(
        self,
        session: Session,
        mapper: BudgetAllocationMatchMapper | None = None,
    ) -> None:
        super().__init__(session, BudgetAllocationMatchModel)
        self._mapper = mapper or BudgetAllocationMatchMapper()

    def add(self, match: BudgetAllocationMatch) -> BudgetAllocationMatch:
        model = self._mapper.to_model(match)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def list_by_allocation(
        self,
        organization_id: UUID,
        budget_allocation_id: UUID,
    ) -> list[BudgetAllocationMatch]:
        stmt = (
            select(BudgetAllocationMatchModel)
            .where(
                BudgetAllocationMatchModel.organization_id == organization_id,
                BudgetAllocationMatchModel.budget_allocation_id == budget_allocation_id,
            )
            .order_by(BudgetAllocationMatchModel.created_at.asc())
        )
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def list_by_budget(
        self,
        organization_id: UUID,
        budget_id: UUID,
    ) -> list[BudgetAllocationMatch]:
        stmt = (
            select(BudgetAllocationMatchModel)
            .join(
                BudgetAllocationModel,
                BudgetAllocationModel.id == BudgetAllocationMatchModel.budget_allocation_id,
            )
            .where(
                BudgetAllocationMatchModel.organization_id == organization_id,
                BudgetAllocationModel.budget_id == budget_id,
            )
            .order_by(BudgetAllocationMatchModel.created_at.asc())
        )
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def sum_matched_amount(
        self,
        organization_id: UUID,
        budget_allocation_id: UUID,
    ) -> Decimal:
        stmt = select(func.coalesce(func.sum(BudgetAllocationMatchModel.matched_amount), 0)).where(
            BudgetAllocationMatchModel.organization_id == organization_id,
            BudgetAllocationMatchModel.budget_allocation_id == budget_allocation_id,
        )
        return Decimal(str(self.session.scalar(stmt) or 0))

    def remove(self, match: BudgetAllocationMatch) -> None:
        model = self.session.get(BudgetAllocationMatchModel, match.id)
        if model is None or model.organization_id != match.organization_id:
            raise LookupError("Budget allocation match not found for remove.")
        self.delete(model)
        self.flush()
