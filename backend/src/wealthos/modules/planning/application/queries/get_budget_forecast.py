"""GetBudgetForecast query."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.planning.application.services.budget_forecast_service import (
    BudgetForecast,
    BudgetForecastService,
    ForecastAllocationInput,
)
from wealthos.modules.planning.domain.exceptions import BudgetNotFoundError
from wealthos.modules.planning.domain.repositories.budget_allocation_repository import (
    BudgetAllocationRepository,
)
from wealthos.modules.planning.domain.repositories.budget_repository import BudgetRepository
from wealthos.modules.planning.domain.repositories.planning_read_repository import (
    PlanningReadRepository,
)


class GetBudgetForecastQuery:
    def __init__(
        self,
        budgets: BudgetRepository,
        allocations: BudgetAllocationRepository,
        read: PlanningReadRepository,
        forecast: BudgetForecastService | None = None,
    ) -> None:
        self._budgets = budgets
        self._allocations = allocations
        self._read = read
        self._forecast = forecast or BudgetForecastService()

    def execute(
        self,
        organization_id: UUID,
        budget_id: UUID,
        *,
        as_of: date | None = None,
    ) -> BudgetForecast:
        budget = self._budgets.get_by_id(organization_id, budget_id)
        if budget is None:
            raise BudgetNotFoundError("Budget not found.")

        allocations = self._allocations.list_by_budget(organization_id, budget_id)
        actuals = self._read.get_budget_actuals(
            organization_id,
            budget_id,
            date_from=budget.date_from,
            date_to=budget.date_to,
            currency=budget.currency,
        )
        by_category = {
            (row.category_id, row.allocation_type): row.actual_amount for row in actuals.by_category
        }

        rows: list[ForecastAllocationInput] = []
        for allocation in allocations:
            key = (allocation.category_id, allocation.allocation_type.value)
            actual = by_category.get(key, Decimal("0.00"))
            if allocation.debt_id is not None:
                actual = self._read.get_debt_payment_actuals(
                    organization_id,
                    allocation.debt_id,
                    date_from=budget.date_from,
                    date_to=budget.date_to,
                )
            elif allocation.tax_profile_id is not None:
                actual = self._read.get_tax_payment_actuals(
                    organization_id,
                    allocation.tax_profile_id,
                    date_from=budget.date_from,
                    date_to=budget.date_to,
                )
            rows.append(
                ForecastAllocationInput(
                    allocation_id=allocation.id,
                    allocation_type=allocation.allocation_type.value,
                    planned_amount=allocation.amount.amount,
                    actual_to_date=actual,
                )
            )

        return self._forecast.forecast(
            date_from=budget.date_from,
            date_to=budget.date_to,
            as_of=as_of or date.today(),
            allocations=rows,
        )
