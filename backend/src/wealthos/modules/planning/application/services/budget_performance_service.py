"""Budget performance and allocation status (pure Decimal math)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from wealthos.modules.planning.application.services.budget_pace_service import (
    BudgetPaceService,
    PaceAnalysis,
)

_ZERO = Decimal("0.00")
_CENT = Decimal("0.01")
_HUNDRED = Decimal("100")
_PACE_WARNING_POINTS = Decimal("20.00")
_UTIL_WARNING = Decimal("0.80")


@dataclass(frozen=True, slots=True)
class AllocationPerformanceInput:
    allocation_id: UUID
    allocation_type: str
    planned_amount: Decimal
    actual_amount: Decimal


@dataclass(frozen=True, slots=True)
class BudgetAllocationPerformance:
    allocation_id: UUID
    allocation_type: str
    planned_amount: Decimal
    actual_amount: Decimal
    variance_amount: Decimal
    utilization_percentage: Decimal | None
    status: str


@dataclass(frozen=True, slots=True)
class BudgetPerformanceSummary:
    planned_income: Decimal
    actual_income: Decimal
    income_variance: Decimal
    planned_expenses: Decimal
    actual_expenses: Decimal
    expense_variance: Decimal
    planned_surplus: Decimal
    actual_surplus: Decimal
    surplus_variance: Decimal
    allocations: tuple[BudgetAllocationPerformance, ...]
    pace: PaceAnalysis | None = None


class BudgetPerformanceService:
    """Compute income/expense/surplus variances and allocation statuses."""

    def __init__(self, pace_service: BudgetPaceService | None = None) -> None:
        self._pace = pace_service or BudgetPaceService()

    def analyze(
        self,
        *,
        date_from: date,
        date_to: date,
        as_of: date,
        allocations: tuple[AllocationPerformanceInput, ...] | list[AllocationPerformanceInput],
    ) -> BudgetPerformanceSummary:
        planned_income = _ZERO
        actual_income = _ZERO
        planned_expenses = _ZERO
        actual_expenses = _ZERO

        income_types = {"income"}
        expense_types = {"expense", "debt_payment", "tax_reserve", "goal_contribution", "savings"}

        for row in allocations:
            planned = _money(row.planned_amount)
            actual = _money(row.actual_amount)
            if row.allocation_type in income_types:
                planned_income += planned
                actual_income += actual
            elif row.allocation_type in expense_types:
                planned_expenses += planned
                actual_expenses += actual

        planned_surplus = planned_income - planned_expenses
        actual_surplus = actual_income - actual_expenses

        pace = self._pace.analyze(
            date_from,
            date_to,
            as_of,
            planned_expenses,
            actual_expenses,
        )

        performances = tuple(
            self._allocation_performance(row, date_from, date_to, as_of, pace)
            for row in allocations
        )

        return BudgetPerformanceSummary(
            planned_income=_money(planned_income),
            actual_income=_money(actual_income),
            income_variance=_money(actual_income - planned_income),
            planned_expenses=_money(planned_expenses),
            actual_expenses=_money(actual_expenses),
            expense_variance=_money(planned_expenses - actual_expenses),
            planned_surplus=_money(planned_surplus),
            actual_surplus=_money(actual_surplus),
            surplus_variance=_money(actual_surplus - planned_surplus),
            allocations=performances,
            pace=pace,
        )

    def income_variance(self, planned: Decimal, actual: Decimal) -> Decimal:
        return _money(Decimal(str(actual)) - Decimal(str(planned)))

    def expense_variance(self, planned: Decimal, actual: Decimal) -> Decimal:
        return _money(Decimal(str(planned)) - Decimal(str(actual)))

    def surplus_variance(
        self,
        *,
        planned_income: Decimal,
        planned_expenses: Decimal,
        actual_income: Decimal,
        actual_expenses: Decimal,
    ) -> Decimal:
        planned_surplus = Decimal(str(planned_income)) - Decimal(str(planned_expenses))
        actual_surplus = Decimal(str(actual_income)) - Decimal(str(actual_expenses))
        return _money(actual_surplus - planned_surplus)

    def _allocation_performance(
        self,
        row: AllocationPerformanceInput,
        date_from: date,
        date_to: date,
        as_of: date,
        pace: PaceAnalysis,
    ) -> BudgetAllocationPerformance:
        planned = _money(row.planned_amount)
        actual = _money(row.actual_amount)
        is_income = row.allocation_type == "income"

        if is_income:
            variance = _money(actual - planned)
        else:
            variance = _money(planned - actual)

        if planned <= _ZERO:
            utilization: Decimal | None = None
            status = "not_started" if actual <= _ZERO else "completed"
        else:
            utilization = ((actual * _HUNDRED) / planned).quantize(
                _CENT,
                rounding=ROUND_HALF_UP,
            )
            util_ratio = actual / planned
            status = _status_for_allocation(
                is_income=is_income,
                util_ratio=util_ratio,
                utilization_pct=utilization,
                elapsed_pct=pace.elapsed_percentage,
                as_of=as_of,
                date_from=date_from,
                date_to=date_to,
                actual=actual,
            )

        return BudgetAllocationPerformance(
            allocation_id=row.allocation_id,
            allocation_type=row.allocation_type,
            planned_amount=planned,
            actual_amount=actual,
            variance_amount=variance,
            utilization_percentage=utilization,
            status=status,
        )


def _status_for_allocation(
    *,
    is_income: bool,
    util_ratio: Decimal,
    utilization_pct: Decimal,
    elapsed_pct: Decimal,
    as_of: date,
    date_from: date,
    date_to: date,
    actual: Decimal,
) -> str:
    if as_of < date_from and actual <= _ZERO:
        return "not_started"

    if is_income:
        if util_ratio >= Decimal("1"):
            return "completed"
        # Income is on track when it keeps pace with elapsed time.
        if utilization_pct + Decimal("5.00") >= elapsed_pct:
            return "on_track"
        return "warning"

    # Expenses
    if util_ratio >= Decimal("1"):
        return "over_budget"

    pace_variance = utilization_pct - elapsed_pct
    if util_ratio >= _UTIL_WARNING or pace_variance >= _PACE_WARNING_POINTS:
        return "warning"

    if as_of > date_to and util_ratio < Decimal("1"):
        return "on_track"

    return "on_track"


def _money(value: Decimal | int | str) -> Decimal:
    return Decimal(str(value)).quantize(_CENT, rounding=ROUND_HALF_UP)
