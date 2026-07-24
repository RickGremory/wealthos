"""RemoveBudgetAllocation command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.planning.domain.exceptions import (
    BudgetAllocationNotFoundError,
    BudgetNotFoundError,
)
from wealthos.modules.planning.domain.repositories.budget_allocation_repository import (
    BudgetAllocationRepository,
)
from wealthos.modules.planning.domain.repositories.budget_repository import BudgetRepository


@dataclass(frozen=True, slots=True)
class RemoveBudgetAllocationInput:
    organization_id: UUID
    budget_id: UUID
    allocation_id: UUID


class RemoveBudgetAllocationCommand:
    def __init__(
        self,
        budgets: BudgetRepository,
        allocations: BudgetAllocationRepository,
    ) -> None:
        self._budgets = budgets
        self._allocations = allocations

    def execute(self, data: RemoveBudgetAllocationInput) -> None:
        budget = self._budgets.get_by_id(data.organization_id, data.budget_id)
        if budget is None:
            raise BudgetNotFoundError("Budget not found.")
        budget.ensure_allocations_editable()

        allocation = self._allocations.get_by_id(data.organization_id, data.allocation_id)
        if allocation is None or allocation.budget_id != data.budget_id:
            raise BudgetAllocationNotFoundError("Budget allocation not found.")
        self._allocations.remove(allocation)
