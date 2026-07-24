"""UpdateBudgetAllocation command."""

from __future__ import annotations

from dataclasses import dataclass, field
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
from wealthos.modules.planning.domain.exceptions import (
    BudgetAllocationNotFoundError,
    BudgetNotFoundError,
)
from wealthos.modules.planning.domain.repositories.budget_allocation_repository import (
    BudgetAllocationRepository,
)
from wealthos.modules.planning.domain.repositories.budget_repository import BudgetRepository
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class UpdateBudgetAllocationInput:
    organization_id: UUID
    budget_id: UUID
    allocation_id: UUID
    amount: Decimal | None = None
    notes: str | None = None
    category_id: UUID | None = None
    goal_id: UUID | None = None
    debt_id: UUID | None = None
    tax_profile_id: UUID | None = None
    destination_account_id: UUID | None = None
    fields_set: frozenset[str] = field(default_factory=frozenset)


class UpdateBudgetAllocationCommand:
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

    def execute(self, data: UpdateBudgetAllocationInput) -> BudgetAllocation:
        budget = self._budgets.get_by_id(data.organization_id, data.budget_id)
        if budget is None:
            raise BudgetNotFoundError("Budget not found.")
        budget.ensure_allocations_editable()

        allocation = self._allocations.get_by_id(data.organization_id, data.allocation_id)
        if allocation is None or allocation.budget_id != data.budget_id:
            raise BudgetAllocationNotFoundError("Budget allocation not found.")

        currency = budget.currency.value
        if "amount" in data.fields_set and data.amount is not None:
            allocation.update_amount(Money(data.amount, currency))
        if "notes" in data.fields_set:
            allocation.update_notes(data.notes)
        if "category_id" in data.fields_set:
            if data.category_id is not None:
                self._validator.ensure_category(data.organization_id, data.category_id)
            allocation.update_category(data.category_id)
        if "goal_id" in data.fields_set:
            if data.goal_id is not None:
                self._validator.ensure_goal(data.organization_id, data.goal_id, currency)
            allocation.update_goal(data.goal_id)
        if "debt_id" in data.fields_set:
            if data.debt_id is not None:
                self._validator.ensure_debt(data.organization_id, data.debt_id, currency)
            allocation.update_debt(data.debt_id)
        if "tax_profile_id" in data.fields_set:
            if data.tax_profile_id is not None:
                self._validator.ensure_tax_profile(
                    data.organization_id, data.tax_profile_id, currency
                )
            allocation.update_tax_profile(data.tax_profile_id)
        if "destination_account_id" in data.fields_set:
            if data.destination_account_id is not None:
                self._validator.ensure_account(
                    data.organization_id, data.destination_account_id, currency
                )
            allocation.update_destination_account(data.destination_account_id)

        existing = self._allocations.list_by_budget(data.organization_id, data.budget_id)
        assert_unique_allocation(existing, allocation, exclude_id=allocation.id)
        return self._allocations.save(allocation)
