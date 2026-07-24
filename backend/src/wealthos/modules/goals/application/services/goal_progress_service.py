"""Derive GoalProgress from strategy-specific sources."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from wealthos.core.timing import timed
from wealthos.modules.goals.application.views.goal_progress import GoalProgress
from wealthos.modules.goals.domain.entities.goal import Goal
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.shared.domain.value_objects.money import Money

_ZERO = Decimal("0.00")
_HUNDRED = Decimal("100")


class GoalProgressService:
    """Single place for goal progress math (never duplicate elsewhere).

    Request-scoped caches avoid N+1 SQL when listing many goals that share
    currency / net-worth / savings windows.
    """

    def __init__(self, repository: GoalRepository) -> None:
        self._repository = repository
        self._manual_cache: dict[UUID, Decimal] = {}
        self._balance_cache: dict[tuple[UUID, frozenset[UUID], str], Decimal] = {}
        self._net_worth_cache: dict[tuple[UUID, str], Decimal] = {}
        self._savings_cache: dict[
            tuple[UUID, str, frozenset[UUID] | None, int],
            Decimal,
        ] = {}

    def calculate(self, goal: Goal) -> GoalProgress:
        with timed(
            "goals.progress",
            goal_id=str(goal.id),
            organization_id=str(goal.organization_id),
            strategy=goal.strategy.value,
        ):
            return self._calculate(goal)

    def calculate_many(self, goals: list[Goal]) -> list[GoalProgress]:
        return [self.calculate(goal) for goal in goals]

    def _calculate(self, goal: Goal) -> GoalProgress:
        currency = goal.target_amount.currency.value
        current = self._current_amount(goal)
        target = goal.target_amount.amount
        remaining = max(target - current, _ZERO)
        if target <= _ZERO:
            percentage = _HUNDRED
        else:
            percentage = min(
                (current * _HUNDRED / target).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                ),
                _HUNDRED,
            )
        estimated = self._estimate_completion(goal, remaining)
        return GoalProgress(
            goal_id=goal.id,
            current_amount=Money(current, currency),
            remaining_amount=Money(remaining, currency),
            completion_percentage=percentage,
            estimated_completion_date=estimated,
        )

    def _current_amount(self, goal: Goal) -> Decimal:
        currency = goal.target_amount.currency.value
        if goal.strategy.is_manual:
            if goal.id not in self._manual_cache:
                stored = self._repository.get_manual_progress(goal.id)
                self._manual_cache[goal.id] = Decimal(str(stored or 0)).quantize(Decimal("0.01"))
            return self._manual_cache[goal.id]
        if goal.strategy.is_linked_accounts:
            key = (
                goal.organization_id,
                frozenset(goal.linked_account_ids),
                currency,
            )
            if key not in self._balance_cache:
                self._balance_cache[key] = self._repository.sum_account_balances(
                    goal.organization_id,
                    goal.linked_account_ids,
                    currency,
                ).quantize(Decimal("0.01"))
            return self._balance_cache[key]

        nw_key = (goal.organization_id, currency)
        if nw_key not in self._net_worth_cache:
            self._net_worth_cache[nw_key] = self._repository.net_worth_for_currency(
                goal.organization_id,
                currency,
            ).quantize(Decimal("0.01"))
        return self._net_worth_cache[nw_key]

    def _estimate_completion(self, goal: Goal, remaining: Decimal) -> date | None:
        if remaining <= _ZERO:
            return datetime.now(UTC).date()
        if goal.strategy.is_manual:
            return None

        account_ids: frozenset[UUID] | None
        if goal.strategy.is_linked_accounts:
            account_ids = frozenset(goal.linked_account_ids)
        else:
            account_ids = None

        daily = self._average_daily_savings(
            goal.organization_id,
            currency=goal.target_amount.currency.value,
            account_ids=account_ids,
        )
        if daily <= _ZERO:
            return None
        days_needed = int((remaining / daily).to_integral_value(rounding=ROUND_HALF_UP))
        days_needed = max(days_needed, 1)
        return (datetime.now(UTC) + timedelta(days=days_needed)).date()

    def _average_daily_savings(
        self,
        organization_id: UUID,
        *,
        currency: str,
        account_ids: frozenset[UUID] | None,
        days: int = 90,
    ) -> Decimal:
        key = (organization_id, currency, account_ids, days)
        if key not in self._savings_cache:
            raw_ids = tuple(sorted(account_ids)) if account_ids is not None else None
            self._savings_cache[key] = self._repository.average_daily_savings(
                organization_id,
                currency=currency,
                account_ids=raw_ids,
                days=days,
            )
        return self._savings_cache[key]
