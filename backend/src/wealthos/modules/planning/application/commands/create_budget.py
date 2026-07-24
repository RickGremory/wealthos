"""CreateBudget command."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from wealthos.modules.planning.domain.entities.budget import Budget
from wealthos.modules.planning.domain.repositories.budget_repository import BudgetRepository


@dataclass(frozen=True, slots=True)
class CreateBudgetInput:
    organization_id: UUID
    name: str
    period_type: str
    currency: str
    rollover_policy: str = "none"
    forecast_method: str = "linear"
    reference_date: date | None = None
    date_from: date | None = None
    date_to: date | None = None


class CreateBudgetCommand:
    def __init__(self, budgets: BudgetRepository) -> None:
        self._budgets = budgets

    def execute(self, data: CreateBudgetInput) -> Budget:
        budget = Budget.create(
            organization_id=data.organization_id,
            name=data.name,
            period_type=data.period_type,
            currency=data.currency,
            rollover_policy=data.rollover_policy,
            forecast_method=data.forecast_method,
            reference_date=data.reference_date,
            date_from=data.date_from,
            date_to=data.date_to,
        )
        return self._budgets.add(budget)
