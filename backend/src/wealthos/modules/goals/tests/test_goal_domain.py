"""Goal domain entity and value object tests."""

from decimal import Decimal
from uuid import uuid4

import pytest

from wealthos.modules.goals.domain.entities.goal import Goal
from wealthos.modules.goals.domain.exceptions import (
    GoalAlreadyArchived,
    GoalAlreadyCompleted,
    InvalidGoalStrategy,
    InvalidTargetAmount,
    LinkedAccountsNotAllowed,
    LinkedAccountsRequired,
)
from wealthos.modules.goals.domain.value_objects.goal_strategy import GoalStrategy
from wealthos.shared.domain.value_objects.money import Money


def test_create_valid_goal() -> None:
    goal = Goal.create(
        organization_id=uuid4(),
        name="Casa",
        target_amount=Money(Decimal("500000.00"), "MXN"),
        strategy="manual",
    )
    assert goal.status.is_active
    assert goal.strategy.is_manual
    assert goal.linked_account_ids == ()
    assert goal.completed_at is None


def test_rejects_non_positive_target() -> None:
    with pytest.raises(InvalidTargetAmount):
        Goal.create(
            organization_id=uuid4(),
            name="Casa",
            target_amount=Money(Decimal("0"), "MXN"),
            strategy="manual",
        )


def test_complete_and_archive() -> None:
    goal = Goal.create(
        organization_id=uuid4(),
        name="Viaje",
        target_amount=Money(Decimal("80000"), "MXN"),
        strategy="manual",
    )
    goal.complete()
    assert goal.status.is_completed
    assert goal.completed_at is not None
    with pytest.raises(GoalAlreadyCompleted):
        goal.complete()

    goal.archive()
    assert goal.status.is_archived
    with pytest.raises(GoalAlreadyArchived):
        goal.archive()


def test_linked_accounts_strategy_rules() -> None:
    account_id = uuid4()
    with pytest.raises(LinkedAccountsRequired):
        Goal.create(
            organization_id=uuid4(),
            name="Emergencia",
            target_amount=Money(Decimal("100000"), "MXN"),
            strategy="linked_accounts",
        )

    with pytest.raises(LinkedAccountsNotAllowed):
        Goal.create(
            organization_id=uuid4(),
            name="Viaje",
            target_amount=Money(Decimal("80000"), "MXN"),
            strategy="manual",
            linked_account_ids=(account_id,),
        )

    goal = Goal.create(
        organization_id=uuid4(),
        name="Emergencia",
        target_amount=Money(Decimal("100000"), "MXN"),
        strategy="linked_accounts",
        linked_account_ids=(account_id,),
    )
    assert goal.linked_account_ids == (account_id,)


def test_goal_strategies() -> None:
    assert GoalStrategy("manual").is_manual
    assert GoalStrategy("linked_accounts").is_linked_accounts
    assert GoalStrategy("net_worth_percentage").is_net_worth_percentage
    with pytest.raises(InvalidGoalStrategy):
        GoalStrategy("paused")
