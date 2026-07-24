"""AddBudgetAllocation command."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.modules.planning.application.commands._allocation_uniqueness import (
    assert_unique_allocation,
)
from wealthos.modules.planning.application.commands._linked_resource_validator import (
    LinkedResourceValidator,
)
from wealthos.modules.planning.domain.entities.budget_allocation import BudgetAllocation
from wealthos.modules.planning.domain.exceptions import BudgetNotFoundError
from wealthos.modules.planning.domain.repositories.budget_allocation_repository import (
    BudgetAllocationRepository,
)
from wealthos.modules.planning.domain.repositories.budget_repository import BudgetRepository
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class AddBudgetAllocationInput:
    organization_id: UUID
    budget_id: UUID
    allocation_type: str
    amount: Decimal
    category_id: UUID | None = None
    goal_id: UUID | None = None
    debt_id: UUID | None = None
    tax_profile_id: UUID | None = None
    destination_account_id: UUID | None = None
    notes: str | None = None


class AddBudgetAllocationCommand:
    def __init__(
        self,
        budgets: BudgetRepository,
        allocations: BudgetAllocationRepository,
        accounts: AccountRepository,
        categories: CategoryRepository,
        goals: GoalRepository,
        debts: DebtRepository,
        tax_profiles: TaxProfileRepository,
    ) -> None:
        self._budgets = budgets
        self._allocations = allocations
        self._validator = LinkedResourceValidator(
            accounts=accounts,
            categories=categories,
            goals=goals,
            debts=debts,
            tax_profiles=tax_profiles,
        )

    def execute(self, data: AddBudgetAllocationInput) -> BudgetAllocation:
        budget = self._budgets.get_by_id(data.organization_id, data.budget_id)
        if budget is None:
            raise BudgetNotFoundError("Budget not found.")
        budget.ensure_allocations_editable()

        currency = budget.currency.value
        self._validate_links(data, currency)

        allocation = BudgetAllocation.create(
            organization_id=data.organization_id,
            budget_id=data.budget_id,
            allocation_type=data.allocation_type,
            amount=Money(data.amount, currency),
            category_id=data.category_id,
            goal_id=data.goal_id,
            debt_id=data.debt_id,
            tax_profile_id=data.tax_profile_id,
            destination_account_id=data.destination_account_id,
            notes=data.notes,
        )
        existing = self._allocations.list_by_budget(data.organization_id, data.budget_id)
        assert_unique_allocation(existing, allocation)
        return self._allocations.add(allocation)

    def _validate_links(self, data: AddBudgetAllocationInput, currency: str) -> None:
        if data.category_id is not None:
            self._validator.ensure_category(data.organization_id, data.category_id)
        if data.goal_id is not None:
            self._validator.ensure_goal(data.organization_id, data.goal_id, currency)
        if data.debt_id is not None:
            self._validator.ensure_debt(data.organization_id, data.debt_id, currency)
        if data.tax_profile_id is not None:
            self._validator.ensure_tax_profile(data.organization_id, data.tax_profile_id, currency)
        if data.destination_account_id is not None:
            self._validator.ensure_account(
                data.organization_id, data.destination_account_id, currency
            )
