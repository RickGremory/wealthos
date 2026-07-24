"""Linear budget forecast to period close."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

_ZERO = Decimal("0.00")
_CENT = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class ForecastAllocationInput:
    allocation_id: UUID
    allocation_type: str
    planned_amount: Decimal
    actual_to_date: Decimal


@dataclass(frozen=True, slots=True)
class ForecastAllocationProjection:
    allocation_id: UUID
    allocation_type: str
    planned: Decimal
    actual_to_date: Decimal
    projected_at_close: Decimal
    projected_variance: Decimal


@dataclass(frozen=True, slots=True)
class BudgetForecast:
    projected_income: Decimal
    projected_expenses: Decimal
    projected_surplus: Decimal
    elapsed_days: int
    total_days: int
    allocations: tuple[ForecastAllocationProjection, ...]


class BudgetForecastService:
    """Linear (daily average) projection to budget close."""

    def forecast(
        self,
        *,
        date_from: date,
        date_to: date,
        as_of: date,
        allocations: tuple[ForecastAllocationInput, ...] | list[ForecastAllocationInput],
    ) -> BudgetForecast:
        total_days = max((date_to - date_from).days + 1, 1)
        elapsed_days = _elapsed_days(date_from, date_to, as_of, total_days)

        has_activity = any(Decimal(str(a.actual_to_date)) > _ZERO for a in allocations)
        if 0 < elapsed_days < total_days and has_activity:
            elapsed_for_math = max(elapsed_days, 1)
        elif elapsed_days <= 0:
            elapsed_for_math = 1 if has_activity else 0
        else:
            elapsed_for_math = elapsed_days

        projections: list[ForecastAllocationProjection] = []
        projected_income = _ZERO
        projected_expenses = _ZERO
        income_types = {"income"}
        expense_types = {"expense", "debt_payment", "tax_reserve", "goal_contribution", "savings"}

        for row in allocations:
            planned = _money(row.planned_amount)
            actual = _money(row.actual_to_date)
            projected = _project(actual, elapsed_for_math, total_days)

            if row.allocation_type in income_types:
                projected_income += projected
                projected_variance = _money(projected - planned)
            elif row.allocation_type in expense_types:
                projected_expenses += projected
                projected_variance = _money(planned - projected)
            else:
                projected_variance = _money(projected - planned)

            projections.append(
                ForecastAllocationProjection(
                    allocation_id=row.allocation_id,
                    allocation_type=row.allocation_type,
                    planned=planned,
                    actual_to_date=actual,
                    projected_at_close=projected,
                    projected_variance=projected_variance,
                )
            )

        return BudgetForecast(
            projected_income=_money(projected_income),
            projected_expenses=_money(projected_expenses),
            projected_surplus=_money(projected_income - projected_expenses),
            elapsed_days=elapsed_days,
            total_days=total_days,
            allocations=tuple(projections),
        )


def _project(actual: Decimal, elapsed_days: int, total_days: int) -> Decimal:
    if elapsed_days <= 0:
        return _ZERO
    daily = (actual / Decimal(elapsed_days)).quantize(
        Decimal("0.0001"),
        rounding=ROUND_HALF_UP,
    )
    return _money(daily * Decimal(total_days))


def _elapsed_days(date_from: date, date_to: date, as_of: date, total_days: int) -> int:
    if as_of < date_from:
        return 0
    if as_of > date_to:
        return total_days
    return (as_of - date_from).days + 1


def _money(value: Decimal | int | str) -> Decimal:
    return Decimal(str(value)).quantize(_CENT, rounding=ROUND_HALF_UP)
