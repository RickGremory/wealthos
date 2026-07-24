"""Budget pace analysis (elapsed time vs spending)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

_ZERO = Decimal("0.00")
_HUNDRED = Decimal("100")
_CENT = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class PaceAnalysis:
    elapsed_percentage: Decimal
    spending_percentage: Decimal | None
    pace_variance: Decimal | None
    total_days: int
    elapsed_days: int


class BudgetPaceService:
    """Compare spending progress against calendar progress."""

    def analyze(
        self,
        date_from: date,
        date_to: date,
        as_of: date,
        planned_expense: Decimal,
        actual_expense: Decimal,
    ) -> PaceAnalysis:
        total_days = max((date_to - date_from).days + 1, 1)
        elapsed_days = _elapsed_days(date_from, date_to, as_of, total_days)
        elapsed_pct = _pct(Decimal(elapsed_days), Decimal(total_days))

        planned = Decimal(str(planned_expense))
        actual = Decimal(str(actual_expense))

        if planned <= _ZERO:
            spending_pct: Decimal | None = None
            pace_variance: Decimal | None = None
        else:
            spending_pct = _pct(actual, planned)
            pace_variance = (spending_pct - elapsed_pct).quantize(
                _CENT,
                rounding=ROUND_HALF_UP,
            )

        return PaceAnalysis(
            elapsed_percentage=elapsed_pct,
            spending_percentage=spending_pct,
            pace_variance=pace_variance,
            total_days=total_days,
            elapsed_days=elapsed_days,
        )


def _elapsed_days(date_from: date, date_to: date, as_of: date, total_days: int) -> int:
    if as_of < date_from:
        return 0
    if as_of > date_to:
        return total_days
    return (as_of - date_from).days + 1


def _pct(numerator: Decimal, denominator: Decimal) -> Decimal:
    return ((numerator * _HUNDRED) / denominator).quantize(_CENT, rounding=ROUND_HALF_UP)
