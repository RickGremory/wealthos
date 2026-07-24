"""SQLAlchemy BudgetRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.planning.domain.entities.budget import Budget
from wealthos.modules.planning.infrastructure.mappers.budget_mapper import BudgetMapper
from wealthos.modules.planning.infrastructure.models.planning_models import BudgetModel
from wealthos.shared.base import BaseRepository


class SqlAlchemyBudgetRepository(BaseRepository[BudgetModel]):
    def __init__(self, session: Session, mapper: BudgetMapper | None = None) -> None:
        super().__init__(session, BudgetModel)
        self._mapper = mapper or BudgetMapper()

    def add(self, budget: Budget) -> Budget:
        model = self._mapper.to_model(budget)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(self, organization_id: UUID, budget_id: UUID) -> Budget | None:
        stmt = select(BudgetModel).where(
            BudgetModel.organization_id == organization_id,
            BudgetModel.id == budget_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        status: str | None = None,
        currency: str | None = None,
        include_archived: bool = False,
    ) -> list[Budget]:
        stmt = select(BudgetModel).where(BudgetModel.organization_id == organization_id)
        if status is not None:
            stmt = stmt.where(BudgetModel.status == status)
        elif not include_archived:
            stmt = stmt.where(BudgetModel.status != "archived")
        if currency is not None:
            stmt = stmt.where(BudgetModel.currency == currency)
        stmt = stmt.order_by(BudgetModel.created_at.desc())
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def save(self, budget: Budget) -> Budget:
        model = self.session.get(BudgetModel, budget.id)
        if model is None or model.organization_id != budget.organization_id:
            raise LookupError("Budget not found for save.")
        self._mapper.apply_to_model(budget, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)
