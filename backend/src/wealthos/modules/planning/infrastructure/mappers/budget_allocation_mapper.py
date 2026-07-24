"""Map BudgetAllocation ↔ BudgetAllocationModel."""

from __future__ import annotations

from wealthos.modules.planning.domain.entities.budget_allocation import BudgetAllocation
from wealthos.modules.planning.domain.value_objects.budget_allocation_type import (
    BudgetAllocationType,
)
from wealthos.modules.planning.infrastructure.models.planning_models import (
    BudgetAllocationModel,
)
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class BudgetAllocationMapper(BaseMapper[BudgetAllocationModel, BudgetAllocation]):
    def to_entity(self, model: BudgetAllocationModel) -> BudgetAllocation:
        return BudgetAllocation(
            id=model.id,
            organization_id=model.organization_id,
            budget_id=model.budget_id,
            allocation_type=BudgetAllocationType(model.allocation_type),
            category_id=model.category_id,
            goal_id=model.goal_id,
            debt_id=model.debt_id,
            tax_profile_id=model.tax_profile_id,
            destination_account_id=model.destination_account_id,
            amount=Money(model.amount, model.currency),
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: BudgetAllocation) -> BudgetAllocationModel:
        return BudgetAllocationModel(
            id=entity.id,
            organization_id=entity.organization_id,
            budget_id=entity.budget_id,
            allocation_type=entity.allocation_type.value,
            category_id=entity.category_id,
            goal_id=entity.goal_id,
            debt_id=entity.debt_id,
            tax_profile_id=entity.tax_profile_id,
            destination_account_id=entity.destination_account_id,
            amount=entity.amount.amount,
            currency=entity.amount.currency.value,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def apply_to_model(
        self,
        entity: BudgetAllocation,
        model: BudgetAllocationModel,
    ) -> BudgetAllocationModel:
        model.allocation_type = entity.allocation_type.value
        model.category_id = entity.category_id
        model.goal_id = entity.goal_id
        model.debt_id = entity.debt_id
        model.tax_profile_id = entity.tax_profile_id
        model.destination_account_id = entity.destination_account_id
        model.amount = entity.amount.amount
        model.currency = entity.amount.currency.value
        model.notes = entity.notes
        model.updated_at = entity.updated_at
        return model
