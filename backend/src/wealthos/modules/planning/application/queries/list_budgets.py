"""ListBudgets query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.planning.domain.entities.budget import Budget
from wealthos.modules.planning.domain.repositories.budget_repository import BudgetRepository


class ListBudgetsQuery:
    def __init__(self, budgets: BudgetRepository) -> None:
        self._budgets = budgets

    def execute(
        self,
        organization_id: UUID,
        *,
        status: str | None = None,
        currency: str | None = None,
        include_archived: bool = False,
    ) -> list[Budget]:
        return self._budgets.list_by_organization(
            organization_id,
            status=status,
            currency=currency,
            include_archived=include_archived,
        )
