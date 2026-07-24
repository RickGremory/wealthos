"""GetBudget query."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.planning.domain.entities.budget import Budget
from wealthos.modules.planning.domain.entities.budget_allocation import BudgetAllocation
from wealthos.modules.planning.domain.exceptions import BudgetNotFoundError
from wealthos.modules.planning.domain.repositories.budget_allocation_repository import (
    BudgetAllocationRepository,
)
from wealthos.modules.planning.domain.repositories.budget_repository import BudgetRepository


@dataclass(frozen=True, slots=True)
class BudgetDetail:
    budget: Budget
    allocations: tuple[BudgetAllocation, ...]


class GetBudgetQuery:
    def __init__(
        self,
        budgets: BudgetRepository,
        allocations: BudgetAllocationRepository,
    ) -> None:
        self._budgets = budgets
        self._allocations = allocations

    def execute(self, organization_id: UUID, budget_id: UUID) -> BudgetDetail:
        budget = self._budgets.get_by_id(organization_id, budget_id)
        if budget is None:
            raise BudgetNotFoundError("Budget not found.")
        allocations = self._allocations.list_by_budget(organization_id, budget_id)
        return BudgetDetail(budget=budget, allocations=tuple(allocations))
