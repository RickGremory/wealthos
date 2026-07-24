"""BudgetPerformanceService variance and status tests."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from wealthos.modules.planning.application.services.budget_performance_service import (
    AllocationPerformanceInput,
    BudgetPerformanceService,
)


def test_income_and_expense_variance_conventions() -> None:
    service = BudgetPerformanceService()
    summary = service.analyze(
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 31),
        as_of=date(2026, 8, 15),
        allocations=(
            AllocationPerformanceInput(
                allocation_id=uuid4(),
                allocation_type="income",
                planned_amount=Decimal("80000.00"),
                actual_amount=Decimal("70000.00"),
            ),
            AllocationPerformanceInput(
                allocation_id=uuid4(),
                allocation_type="expense",
                planned_amount=Decimal("40000.00"),
                actual_amount=Decimal("35000.00"),
            ),
        ),
    )

    assert summary.income_variance == Decimal("-10000.00")
    assert summary.expense_variance == Decimal("5000.00")
    assert summary.planned_surplus == Decimal("40000.00")
    assert summary.actual_surplus == Decimal("35000.00")
    assert summary.surplus_variance == Decimal("-5000.00")


def test_expense_over_budget_and_warning_thresholds() -> None:
    service = BudgetPerformanceService()
    over = service.analyze(
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 31),
        as_of=date(2026, 8, 20),
        allocations=(
            AllocationPerformanceInput(
                allocation_id=uuid4(),
                allocation_type="expense",
                planned_amount=Decimal("8000.00"),
                actual_amount=Decimal("9000.00"),
            ),
        ),
    )
    assert over.allocations[0].status == "over_budget"
    assert over.allocations[0].utilization_percentage == Decimal("112.50")

    warning = service.analyze(
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 31),
        as_of=date(2026, 8, 5),
        allocations=(
            AllocationPerformanceInput(
                allocation_id=uuid4(),
                allocation_type="expense",
                planned_amount=Decimal("10000.00"),
                actual_amount=Decimal("8500.00"),
            ),
        ),
    )
    assert warning.allocations[0].status == "warning"


def test_zero_planned_allocation_status() -> None:
    service = BudgetPerformanceService()
    empty = service.analyze(
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 31),
        as_of=date(2026, 8, 10),
        allocations=(
            AllocationPerformanceInput(
                allocation_id=uuid4(),
                allocation_type="expense",
                planned_amount=Decimal("0.00"),
                actual_amount=Decimal("0.00"),
            ),
            AllocationPerformanceInput(
                allocation_id=uuid4(),
                allocation_type="expense",
                planned_amount=Decimal("0.00"),
                actual_amount=Decimal("100.00"),
            ),
        ),
    )
    assert empty.allocations[0].status == "not_started"
    assert empty.allocations[1].status == "completed"


def test_helper_variance_methods() -> None:
    service = BudgetPerformanceService()
    assert service.income_variance(Decimal("10000"), Decimal("8000")) == Decimal("-2000.00")
    assert service.expense_variance(Decimal("10000"), Decimal("8000")) == Decimal("2000.00")
