"""Unit tests for GoalProgressService."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.goals.application.services.goal_progress_service import (
    GoalProgressService,
)
from wealthos.modules.goals.domain.entities.goal import Goal
from wealthos.shared.domain.value_objects.money import Money


class _FakeGoals:
    def __init__(self) -> None:
        self.manual: dict[UUID, Decimal] = {}
        self.balances: dict[UUID, Decimal] = {}
        self.net_worth: Decimal = Decimal("0.00")
        self.daily_savings: Decimal = Decimal("0.00")

    def get_manual_progress(self, goal_id: UUID) -> Decimal | None:
        return self.manual.get(goal_id)

    def set_manual_progress(self, goal_id: UUID, amount: Decimal) -> None:
        self.manual[goal_id] = amount

    def sum_account_balances(
        self,
        organization_id: UUID,
        account_ids: tuple[UUID, ...],
        currency: str,
    ) -> Decimal:
        _ = organization_id, currency
        return sum(
            (self.balances.get(account_id, Decimal("0.00")) for account_id in account_ids),
            Decimal("0.00"),
        )

    def average_daily_savings(
        self,
        organization_id: UUID,
        *,
        currency: str,
        account_ids: tuple[UUID, ...] | None,
        days: int = 90,
    ) -> Decimal:
        _ = organization_id, currency, account_ids, days
        return self.daily_savings

    def net_worth_for_currency(
        self,
        organization_id: UUID,
        currency: str,
    ) -> Decimal:
        _ = organization_id, currency
        return self.net_worth


def _manual_goal(*, target: str = "100000.00") -> Goal:
    return Goal.create(
        organization_id=uuid4(),
        name="Viaje Japón",
        target_amount=Money(Decimal(target), "MXN"),
        strategy="manual",
    )


def test_manual_progress() -> None:
    repo = _FakeGoals()
    service = GoalProgressService(repo)  # type: ignore[arg-type]
    goal = _manual_goal()
    repo.manual[goal.id] = Decimal("35000.00")

    progress = service.calculate(goal)
    assert progress.current_amount.amount == Decimal("35000.00")
    assert progress.remaining_amount.amount == Decimal("65000.00")
    assert progress.completion_percentage == Decimal("35.00")
    assert progress.estimated_completion_date is None


def test_linked_accounts_sums_balances() -> None:
    repo = _FakeGoals()
    service = GoalProgressService(repo)  # type: ignore[arg-type]
    a1, a2 = uuid4(), uuid4()
    repo.balances[a1] = Decimal("20000.00")
    repo.balances[a2] = Decimal("22500.00")
    goal = Goal.create(
        organization_id=uuid4(),
        name="Fondo emergencia",
        target_amount=Money(Decimal("100000"), "MXN"),
        strategy="linked_accounts",
        linked_account_ids=(a1, a2),
    )
    progress = service.calculate(goal)
    assert progress.current_amount.amount == Decimal("42500.00")
    assert progress.completion_percentage == Decimal("42.50")


def test_net_worth_uses_repository() -> None:
    repo = _FakeGoals()
    service = GoalProgressService(repo)  # type: ignore[arg-type]
    repo.net_worth = Decimal("1250000.00")
    goal = Goal.create(
        organization_id=uuid4(),
        name="FIRE",
        target_amount=Money(Decimal("5000000"), "MXN"),
        strategy="net_worth_percentage",
    )
    progress = service.calculate(goal)
    assert progress.current_amount.amount == Decimal("1250000.00")
    assert progress.completion_percentage == Decimal("25.00")


def test_exceeded_goal_caps_at_100() -> None:
    repo = _FakeGoals()
    service = GoalProgressService(repo)  # type: ignore[arg-type]
    goal = _manual_goal(target="100000.00")
    repo.manual[goal.id] = Decimal("125000.00")
    progress = service.calculate(goal)
    assert progress.completion_percentage == Decimal("100")
    assert progress.remaining_amount.amount == Decimal("0.00")
    assert progress.estimated_completion_date == datetime.now(UTC).date()


def test_estimated_completion_null_when_no_savings() -> None:
    repo = _FakeGoals()
    service = GoalProgressService(repo)  # type: ignore[arg-type]
    account_id = uuid4()
    repo.balances[account_id] = Decimal("40000.00")
    repo.daily_savings = Decimal("0.00")
    goal = Goal.create(
        organization_id=uuid4(),
        name="Casa",
        target_amount=Money(Decimal("100000"), "MXN"),
        strategy="linked_accounts",
        linked_account_ids=(account_id,),
    )
    assert service.calculate(goal).estimated_completion_date is None


def test_estimated_completion_with_positive_average() -> None:
    repo = _FakeGoals()
    service = GoalProgressService(repo)  # type: ignore[arg-type]
    account_id = uuid4()
    repo.balances[account_id] = Decimal("70000.00")
    repo.daily_savings = Decimal("500.00")
    goal = Goal.create(
        organization_id=uuid4(),
        name="Casa",
        target_amount=Money(Decimal("100000"), "MXN"),
        strategy="linked_accounts",
        linked_account_ids=(account_id,),
    )
    estimated = service.calculate(goal).estimated_completion_date
    assert estimated == datetime.now(UTC).date() + timedelta(days=60)
