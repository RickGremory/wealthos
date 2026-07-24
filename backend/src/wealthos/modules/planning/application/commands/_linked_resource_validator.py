"""Validate linked accounts/categories/goals/debts/tax profiles for planning."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.modules.planning.domain.exceptions import (
    LinkedResourceCurrencyMismatch,
    LinkedResourceNotFound,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)


class LinkedResourceValidator:
    def __init__(
        self,
        accounts: AccountRepository | None = None,
        categories: CategoryRepository | None = None,
        goals: GoalRepository | None = None,
        debts: DebtRepository | None = None,
        tax_profiles: TaxProfileRepository | None = None,
    ) -> None:
        self._accounts = accounts
        self._categories = categories
        self._goals = goals
        self._debts = debts
        self._tax_profiles = tax_profiles

    def ensure_account(
        self,
        organization_id: UUID,
        account_id: UUID,
        currency: str,
        *,
        require_active: bool = True,
    ) -> None:
        if self._accounts is None:
            raise RuntimeError("AccountRepository is required.")
        account = self._accounts.get_by_id(organization_id, account_id)
        if account is None:
            raise LinkedResourceNotFound("Linked account not found.")
        if require_active and not account.is_active:
            raise LinkedResourceNotFound("Linked account is archived.")
        if account.currency.value != currency:
            raise LinkedResourceCurrencyMismatch(
                "Linked account currency must match the planning currency."
            )

    def ensure_category(self, organization_id: UUID, category_id: UUID) -> None:
        if self._categories is None:
            raise RuntimeError("CategoryRepository is required.")
        category = self._categories.get_by_id(organization_id, category_id)
        if category is None or not category.is_active:
            raise LinkedResourceNotFound("Linked category not found.")

    def ensure_goal(
        self,
        organization_id: UUID,
        goal_id: UUID,
        currency: str,
    ) -> None:
        if self._goals is None:
            raise RuntimeError("GoalRepository is required.")
        goal = self._goals.get_by_id(organization_id, goal_id)
        if goal is None:
            raise LinkedResourceNotFound("Linked goal not found.")
        if goal.status.is_archived:
            raise LinkedResourceNotFound("Linked goal is archived.")
        if goal.target_amount.currency.value != currency:
            raise LinkedResourceCurrencyMismatch(
                "Linked goal currency must match the budget currency."
            )

    def ensure_debt(
        self,
        organization_id: UUID,
        debt_id: UUID,
        currency: str,
    ) -> None:
        if self._debts is None:
            raise RuntimeError("DebtRepository is required.")
        debt = self._debts.get_by_id(organization_id, debt_id)
        if debt is None:
            raise LinkedResourceNotFound("Linked debt not found.")
        if debt.status.is_archived:
            raise LinkedResourceNotFound("Linked debt is archived.")
        if debt.minimum_payment.currency.value != currency:
            raise LinkedResourceCurrencyMismatch(
                "Linked debt currency must match the planning currency."
            )

    def ensure_tax_profile(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        currency: str,
    ) -> None:
        if self._tax_profiles is None:
            raise RuntimeError("TaxProfileRepository is required.")
        profile = self._tax_profiles.get_by_id(organization_id, tax_profile_id)
        if profile is None:
            raise LinkedResourceNotFound("Linked tax profile not found.")
        if profile.currency.value != currency:
            raise LinkedResourceCurrencyMismatch(
                "Linked tax profile currency must match the budget currency."
            )
