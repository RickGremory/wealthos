"""Derive GoalProgress from strategy-specific sources."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from wealthos.core.timing import timed
from wealthos.modules.goals.application.views.goal_progress import GoalProgress
from wealthos.modules.goals.domain.entities.goal import Goal
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.shared.domain.value_objects.money import Money

_ZERO = Decimal("0.00")
_HUNDRED = Decimal("100")


class GoalProgressService:
    """Single place for goal progress math (never duplicate elsewhere)."""

    def __init__(self, repository: GoalRepository) -> None:
        self._repository = repository

    def calculate(self, goal: Goal) -> GoalProgress:
        with timed(
            "goals.progress",
            goal_id=str(goal.id),
            organization_id=str(goal.organization_id),
            strategy=goal.strategy.value,
        ):
            return self._calculate(goal)

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
            stored = self._repository.get_manual_progress(goal.id)
            return Decimal(str(stored or 0)).quantize(Decimal("0.01"))
        if goal.strategy.is_linked_accounts:
            return self._repository.sum_account_balances(
                goal.organization_id,
                goal.linked_account_ids,
                currency,
            ).quantize(Decimal("0.01"))
        return self._repository.net_worth_for_currency(
            goal.organization_id,
            currency,
        ).quantize(Decimal("0.01"))

    def _estimate_completion(self, goal: Goal, remaining: Decimal) -> date | None:
        if remaining <= _ZERO:
            return datetime.now(UTC).date()
        if goal.strategy.is_manual:
            return None

        account_ids: tuple | None
        if goal.strategy.is_linked_accounts:
            account_ids = goal.linked_account_ids
        else:
            account_ids = None

        daily = self._repository.average_daily_savings(
            goal.organization_id,
            currency=goal.target_amount.currency.value,
            account_ids=account_ids,
        )
        if daily <= _ZERO:
            return None
        days_needed = int((remaining / daily).to_integral_value(rounding=ROUND_HALF_UP))
        days_needed = max(days_needed, 1)
        return (datetime.now(UTC) + timedelta(days=days_needed)).date()
