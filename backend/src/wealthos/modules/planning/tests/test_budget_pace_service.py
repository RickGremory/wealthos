"""BudgetPaceService edge-case tests."""

from datetime import date
from decimal import Decimal

from wealthos.modules.planning.application.services.budget_pace_service import (
    BudgetPaceService,
)


def test_pace_variance_example() -> None:
    # Day 8 of 31 ≈ 25.81% elapsed; 70% spent → positive pace variance.
    result = BudgetPaceService().analyze(
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 31),
        as_of=date(2026, 8, 8),
        planned_expense=Decimal("10000.00"),
        actual_expense=Decimal("7000.00"),
    )
    assert result.elapsed_percentage == Decimal("25.81")
    assert result.spending_percentage == Decimal("70.00")
    assert result.pace_variance == Decimal("44.19")


def test_before_period_elapsed_is_zero() -> None:
    result = BudgetPaceService().analyze(
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 31),
        as_of=date(2026, 7, 20),
        planned_expense=Decimal("1000.00"),
        actual_expense=Decimal("0.00"),
    )
    assert result.elapsed_days == 0
    assert result.elapsed_percentage == Decimal("0.00")
    assert result.spending_percentage == Decimal("0.00")
    assert result.pace_variance == Decimal("0.00")


def test_after_period_elapsed_is_full() -> None:
    result = BudgetPaceService().analyze(
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 31),
        as_of=date(2026, 9, 5),
        planned_expense=Decimal("1000.00"),
        actual_expense=Decimal("900.00"),
    )
    assert result.elapsed_days == 31
    assert result.elapsed_percentage == Decimal("100.00")
    assert result.spending_percentage == Decimal("90.00")
    assert result.pace_variance == Decimal("-10.00")


def test_zero_planned_leaves_spending_none() -> None:
    result = BudgetPaceService().analyze(
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 31),
        as_of=date(2026, 8, 10),
        planned_expense=Decimal("0.00"),
        actual_expense=Decimal("50.00"),
    )
    assert result.spending_percentage is None
    assert result.pace_variance is None
