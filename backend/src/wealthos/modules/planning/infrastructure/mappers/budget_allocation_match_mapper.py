"""Map BudgetAllocationMatch ↔ BudgetAllocationMatchModel."""

from __future__ import annotations

from wealthos.modules.planning.domain.entities.budget_allocation_match import (
    BudgetAllocationMatch,
)
from wealthos.modules.planning.infrastructure.models.planning_models import (
    BudgetAllocationMatchModel,
)
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class BudgetAllocationMatchMapper(BaseMapper[BudgetAllocationMatchModel, BudgetAllocationMatch]):
    def to_entity(self, model: BudgetAllocationMatchModel) -> BudgetAllocationMatch:
        return BudgetAllocationMatch(
            id=model.id,
            organization_id=model.organization_id,
            budget_allocation_id=model.budget_allocation_id,
            transaction_id=model.transaction_id,
            matched_amount=Money(model.matched_amount, model.currency),
            created_at=model.created_at,
        )

    def to_model(self, entity: BudgetAllocationMatch) -> BudgetAllocationMatchModel:
        return BudgetAllocationMatchModel(
            id=entity.id,
            organization_id=entity.organization_id,
            budget_allocation_id=entity.budget_allocation_id,
            transaction_id=entity.transaction_id,
            matched_amount=entity.matched_amount.amount,
            currency=entity.matched_amount.currency.value,
            created_at=entity.created_at,
        )
