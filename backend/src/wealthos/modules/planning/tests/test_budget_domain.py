"""Budget and BudgetAllocation domain tests (sprint §53)."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from wealthos.modules.planning.domain.entities.budget import Budget
from wealthos.modules.planning.domain.entities.budget_allocation import BudgetAllocation
from wealthos.modules.planning.domain.exceptions import (
    AllocationValidationError,
    BudgetAlreadyArchived,
    BudgetClosed,
    BudgetNotEditable,
    InvalidAllocationAmount,
    InvalidBudgetDateRange,
)
from wealthos.shared.domain.value_objects.money import Money


def _make_budget(**overrides) -> Budget:
    defaults = {
        "organization_id": uuid4(),
        "name": "Presupuesto Julio",
        "period_type": "monthly",
        "currency": "MXN",
        "reference_date": date(2026, 7, 15),
    }
    defaults.update(overrides)
    return Budget.create(**defaults)


def test_create_monthly_budget_derives_period() -> None:
    budget = _make_budget()
    assert budget.status.is_draft
    assert budget.date_from == date(2026, 7, 1)
    assert budget.date_to == date(2026, 7, 31)
    assert budget.currency.value == "MXN"
    assert budget.archived_at is None
    assert budget.closed_at is None


def test_custom_budget_requires_dates_and_rejects_inverted_range() -> None:
    with pytest.raises(InvalidBudgetDateRange):
        Budget.create(
            organization_id=uuid4(),
            name="Custom",
            period_type="custom",
            currency="MXN",
        )
    with pytest.raises(InvalidBudgetDateRange):
        Budget.create(
            organization_id=uuid4(),
            name="Custom",
            period_type="custom",
            currency="MXN",
            date_from=date(2026, 7, 31),
            date_to=date(2026, 7, 1),
        )


def test_activate_close_archive_lifecycle() -> None:
    budget = _make_budget()
    budget.activate()
    assert budget.status.is_active

    with pytest.raises(BudgetNotEditable):
        budget.activate()

    budget.close()
    assert budget.status.is_closed
    assert budget.closed_at is not None

    with pytest.raises(BudgetClosed):
        budget.close()

    budget.archive()
    assert budget.status.is_archived
    assert budget.archived_at is not None

    with pytest.raises(BudgetAlreadyArchived):
        budget.archive()


def test_closed_budget_rejects_allocation_edits() -> None:
    budget = _make_budget()
    budget.activate()
    budget.close()
    with pytest.raises(BudgetClosed):
        budget.ensure_allocations_editable()
    with pytest.raises(BudgetClosed):
        budget.ensure_mutable()


def test_archived_budget_rejects_allocation_edits() -> None:
    budget = _make_budget()
    budget.archive()
    with pytest.raises(BudgetAlreadyArchived):
        budget.ensure_allocations_editable()


def test_allocation_requires_positive_amount() -> None:
    with pytest.raises(InvalidAllocationAmount):
        BudgetAllocation.create(
            organization_id=uuid4(),
            budget_id=uuid4(),
            allocation_type="expense",
            amount=Money(Decimal("0.00"), "MXN"),
            category_id=uuid4(),
        )


def test_income_and_expense_require_category() -> None:
    with pytest.raises(AllocationValidationError):
        BudgetAllocation.create(
            organization_id=uuid4(),
            budget_id=uuid4(),
            allocation_type="income",
            amount=Money(Decimal("1000.00"), "MXN"),
        )
    with pytest.raises(AllocationValidationError):
        BudgetAllocation.create(
            organization_id=uuid4(),
            budget_id=uuid4(),
            allocation_type="expense",
            amount=Money(Decimal("1000.00"), "MXN"),
        )


def test_goal_contribution_requires_goal_id() -> None:
    with pytest.raises(AllocationValidationError):
        BudgetAllocation.create(
            organization_id=uuid4(),
            budget_id=uuid4(),
            allocation_type="goal_contribution",
            amount=Money(Decimal("500.00"), "MXN"),
        )
    allocation = BudgetAllocation.create(
        organization_id=uuid4(),
        budget_id=uuid4(),
        allocation_type="goal_contribution",
        amount=Money(Decimal("500.00"), "MXN"),
        goal_id=uuid4(),
    )
    assert allocation.goal_id is not None


def test_debt_payment_requires_debt_id() -> None:
    with pytest.raises(AllocationValidationError):
        BudgetAllocation.create(
            organization_id=uuid4(),
            budget_id=uuid4(),
            allocation_type="debt_payment",
            amount=Money(Decimal("2000.00"), "MXN"),
        )


def test_unallocated_and_savings_do_not_require_category() -> None:
    unallocated = BudgetAllocation.create(
        organization_id=uuid4(),
        budget_id=uuid4(),
        allocation_type="unallocated",
        amount=Money(Decimal("100.00"), "MXN"),
    )
    savings = BudgetAllocation.create(
        organization_id=uuid4(),
        budget_id=uuid4(),
        allocation_type="savings",
        amount=Money(Decimal("100.00"), "MXN"),
    )
    assert unallocated.category_id is None
    assert savings.category_id is None
