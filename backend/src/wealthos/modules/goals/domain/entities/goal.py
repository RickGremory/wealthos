"""Goal aggregate — financial target with derived progress."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.goals.domain.exceptions import (
    GoalAlreadyArchived,
    GoalAlreadyCompleted,
    InvalidTargetAmount,
    LinkedAccountsNotAllowed,
    LinkedAccountsRequired,
)
from wealthos.modules.goals.domain.value_objects.goal_name import GoalName
from wealthos.modules.goals.domain.value_objects.goal_status import GoalStatus
from wealthos.modules.goals.domain.value_objects.goal_strategy import GoalStrategy
from wealthos.shared.domain.value_objects.money import Money


@dataclass(slots=True)
class Goal:
    id: UUID
    organization_id: UUID
    name: GoalName
    target_amount: Money
    target_date: date | None
    strategy: GoalStrategy
    linked_account_ids: tuple[UUID, ...]
    status: GoalStatus
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    archived_at: datetime | None

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        name: str,
        target_amount: Money,
        strategy: str,
        target_date: date | None = None,
        linked_account_ids: tuple[UUID, ...] | list[UUID] = (),
        goal_id: UUID | None = None,
    ) -> Goal:
        if target_amount.amount <= Decimal("0.00"):
            raise InvalidTargetAmount("Goal target amount must be positive.")

        strategy_vo = GoalStrategy(strategy)
        accounts = tuple(dict.fromkeys(linked_account_ids))
        if strategy_vo.is_linked_accounts and not accounts:
            raise LinkedAccountsRequired("linked_accounts strategy requires at least one account.")
        if not strategy_vo.is_linked_accounts and accounts:
            raise LinkedAccountsNotAllowed(
                "Only linked_accounts strategy may include linked accounts."
            )

        now = datetime.now(UTC)
        return cls(
            id=goal_id or uuid4(),
            organization_id=organization_id,
            name=GoalName(name),
            target_amount=target_amount,
            target_date=target_date,
            strategy=strategy_vo,
            linked_account_ids=accounts,
            status=GoalStatus("active"),
            created_at=now,
            updated_at=now,
            completed_at=None,
            archived_at=None,
        )

    def rename(self, name: str) -> None:
        self.name = GoalName(name)
        self.updated_at = datetime.now(UTC)

    def change_target_amount(self, amount: Money) -> None:
        if amount.currency != self.target_amount.currency:
            raise InvalidTargetAmount("Goal currency cannot be changed.")
        if amount.amount <= Decimal("0.00"):
            raise InvalidTargetAmount("Goal target amount must be positive.")
        self.target_amount = amount
        self.updated_at = datetime.now(UTC)

    def change_target_date(self, target_date: date | None) -> None:
        self.target_date = target_date
        self.updated_at = datetime.now(UTC)

    def replace_linked_accounts(self, account_ids: tuple[UUID, ...] | list[UUID]) -> None:
        if not self.strategy.is_linked_accounts:
            raise LinkedAccountsNotAllowed(
                "Only linked_accounts strategy may include linked accounts."
            )
        accounts = tuple(dict.fromkeys(account_ids))
        if not accounts:
            raise LinkedAccountsRequired("linked_accounts strategy requires at least one account.")
        self.linked_account_ids = accounts
        self.updated_at = datetime.now(UTC)

    def complete(self) -> None:
        if self.status.is_archived:
            raise GoalAlreadyArchived("Cannot complete an archived goal.")
        if self.status.is_completed:
            raise GoalAlreadyCompleted("Goal is already completed.")
        now = datetime.now(UTC)
        self.status = GoalStatus("completed")
        self.completed_at = now
        self.updated_at = now

    def archive(self) -> None:
        if self.status.is_archived:
            raise GoalAlreadyArchived("Goal is already archived.")
        now = datetime.now(UTC)
        self.status = GoalStatus("archived")
        self.archived_at = now
        self.updated_at = now
