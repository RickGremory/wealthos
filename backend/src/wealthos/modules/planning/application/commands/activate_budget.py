"""ActivateBudget command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.planning.domain.entities.budget import Budget
from wealthos.modules.planning.domain.exceptions import BudgetNotFoundError
from wealthos.modules.planning.domain.repositories.budget_repository import BudgetRepository


@dataclass(frozen=True, slots=True)
class ActivateBudgetInput:
    organization_id: UUID
    budget_id: UUID


class ActivateBudgetCommand:
    def __init__(self, budgets: BudgetRepository) -> None:
        self._budgets = budgets

    def execute(self, data: ActivateBudgetInput) -> Budget:
        budget = self._budgets.get_by_id(data.organization_id, data.budget_id)
        if budget is None:
            raise BudgetNotFoundError("Budget not found.")
        budget.activate()
        return self._budgets.save(budget)
