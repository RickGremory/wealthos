"""Derive budget period date ranges from period type."""

from __future__ import annotations

from calendar import monthrange
from datetime import date

from wealthos.modules.planning.domain.exceptions import InvalidBudgetDateRange
from wealthos.modules.planning.domain.value_objects.budget_period_type import BudgetPeriodType


def derive_period_dates(
    period_type: BudgetPeriodType | str,
    reference_date: date | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[date, date]:
    """Return inclusive (date_from, date_to) for the given period type.

    For monthly / quarterly / annual, dates are derived from ``reference_date``
    (default: today). For custom, both ``date_from`` and ``date_to`` are required.
    """
    if isinstance(period_type, BudgetPeriodType):
        period = period_type
    else:
        period = BudgetPeriodType(period_type)
    ref = reference_date or date.today()

    if period.is_custom:
        if date_from is None or date_to is None:
            raise InvalidBudgetDateRange("custom period requires both date_from and date_to.")
        if date_from > date_to:
            raise InvalidBudgetDateRange("date_from must be on or before date_to.")
        return date_from, date_to

    if period.value == "monthly":
        start = date(ref.year, ref.month, 1)
        end = date(ref.year, ref.month, monthrange(ref.year, ref.month)[1])
        return start, end

    if period.value == "quarterly":
        quarter_start_month = ((ref.month - 1) // 3) * 3 + 1
        start = date(ref.year, quarter_start_month, 1)
        end_month = quarter_start_month + 2
        end = date(ref.year, end_month, monthrange(ref.year, end_month)[1])
        return start, end

    # annual
    start = date(ref.year, 1, 1)
    end = date(ref.year, 12, 31)
    return start, end
