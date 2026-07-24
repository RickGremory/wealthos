"""UpdateBudget command."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

from wealthos.modules.planning.domain.entities.budget import Budget
from wealthos.modules.planning.domain.exceptions import BudgetNotFoundError
from wealthos.modules.planning.domain.repositories.budget_repository import BudgetRepository


@dataclass(frozen=True, slots=True)
class UpdateBudgetInput:
    organization_id: UUID
    budget_id: UUID
    name: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    rollover_policy: str | None = None
    forecast_method: str | None = None
    fields_set: frozenset[str] = field(default_factory=frozenset)


class UpdateBudgetCommand:
    def __init__(self, budgets: BudgetRepository) -> None:
        self._budgets = budgets

    def execute(self, data: UpdateBudgetInput) -> Budget:
        budget = self._budgets.get_by_id(data.organization_id, data.budget_id)
        if budget is None:
            raise BudgetNotFoundError("Budget not found.")

        if "name" in data.fields_set and data.name is not None:
            budget.rename(data.name)
        if "date_from" in data.fields_set or "date_to" in data.fields_set:
            budget.change_dates(
                data.date_from if data.date_from is not None else budget.date_from,
                data.date_to if data.date_to is not None else budget.date_to,
            )
        if "rollover_policy" in data.fields_set and data.rollover_policy is not None:
            budget.change_rollover_policy(data.rollover_policy)
        if "forecast_method" in data.fields_set and data.forecast_method is not None:
            budget.change_forecast_method(data.forecast_method)

        return self._budgets.save(budget)
