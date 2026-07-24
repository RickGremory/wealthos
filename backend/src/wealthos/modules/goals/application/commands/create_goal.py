"""CreateGoal command."""

from __future__ import annotations

from dataclasses import dataclass
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
)
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class CreateGoalInput:
    organization_id: UUID
    name: str
    target_amount: Decimal
    currency: str
    strategy: str
    target_date: date | None = None
    linked_account_ids: tuple[UUID, ...] = ()


class CreateGoalCommand:
    def __init__(
        self,
        goals: GoalRepository,
        accounts: AccountRepository,
    ) -> None:
        self._goals = goals
        self._accounts = accounts

    def execute(self, data: CreateGoalInput) -> Goal:
        self._validate_accounts(
            data.organization_id,
            data.currency,
            data.linked_account_ids,
        )
        goal = Goal.create(
            organization_id=data.organization_id,
            name=data.name,
            target_amount=Money(data.target_amount, data.currency),
            strategy=data.strategy,
            target_date=data.target_date,
            linked_account_ids=data.linked_account_ids,
        )
        return self._goals.add(goal)

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
