"""UpdateGoal command (strategy is immutable)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.goals.domain.entities.goal import Goal
from wealthos.modules.goals.domain.exceptions import (
    GoalAccountCurrencyMismatch,
    GoalAccountInactive,
    GoalAccountNotFound,
    GoalNotFoundError,
)
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class UpdateGoalInput:
    organization_id: UUID
    goal_id: UUID
    name: str | None = None
    target_amount: Decimal | None = None
    target_date: date | None = None
    linked_account_ids: tuple[UUID, ...] | None = None
    fields_set: frozenset[str] = field(default_factory=frozenset)


class UpdateGoalCommand:
    def __init__(
        self,
        goals: GoalRepository,
        accounts: AccountRepository,
    ) -> None:
        self._goals = goals
        self._accounts = accounts

    def execute(self, data: UpdateGoalInput) -> Goal:
        goal = self._goals.get_by_id(data.organization_id, data.goal_id)
        if goal is None:
            raise GoalNotFoundError("Goal not found.")

        if "name" in data.fields_set and data.name is not None:
            goal.rename(data.name)
        if "target_amount" in data.fields_set and data.target_amount is not None:
            goal.change_target_amount(
                Money(data.target_amount, goal.target_amount.currency)
            )
        if "target_date" in data.fields_set:
            goal.change_target_date(data.target_date)
        if "linked_account_ids" in data.fields_set and data.linked_account_ids is not None:
            self._validate_accounts(
                data.organization_id,
                goal.target_amount.currency.value,
                data.linked_account_ids,
            )
            goal.replace_linked_accounts(data.linked_account_ids)

        return self._goals.save(goal)

    def _validate_accounts(
        self,
        organization_id: UUID,
        currency: str,
        account_ids: tuple[UUID, ...],
    ) -> None:
        for account_id in account_ids:
            account = self._accounts.get_by_id(organization_id, account_id)
            if account is None:
                raise GoalAccountNotFound("Linked account not found.")
            if not account.is_active:
                raise GoalAccountInactive("Cannot link an archived account.")
            if account.currency.value != currency:
                raise GoalAccountCurrencyMismatch(
                    "Linked account currency must match the goal currency."
                )
