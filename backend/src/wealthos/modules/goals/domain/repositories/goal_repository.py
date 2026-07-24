"""Persistence port for Goal aggregates."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol
from uuid import UUID

from wealthos.modules.goals.domain.entities.goal import Goal


class GoalRepository(Protocol):
    def add(self, goal: Goal) -> Goal: ...

    def get_by_id(self, organization_id: UUID, goal_id: UUID) -> Goal | None: ...

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        include_archived: bool = False,
    ) -> list[Goal]: ...

    def save(self, goal: Goal) -> Goal: ...

    def get_manual_progress(self, goal_id: UUID) -> Decimal | None: ...

    def set_manual_progress(self, goal_id: UUID, amount: Decimal) -> None: ...

    def sum_account_balances(
        self,
        organization_id: UUID,
        account_ids: tuple[UUID, ...],
        currency: str,
    ) -> Decimal: ...

    def average_daily_savings(
        self,
        organization_id: UUID,
        *,
        currency: str,
        account_ids: tuple[UUID, ...] | None,
        days: int = 90,
    ) -> Decimal: ...

    def net_worth_for_currency(
        self,
        organization_id: UUID,
        currency: str,
    ) -> Decimal: ...
