"""Minimum cash buffer calculation."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

_ZERO = Decimal("0.00")
_CENT = Decimal("0.01")


class CashBufferService:
    """Resolve minimum cash buffer from fixed amount or days of expenses."""

    def compute(
        self,
        *,
        buffer_type: str,
        buffer_value: Decimal,
        avg_daily_expense: Decimal = Decimal("0"),
    ) -> Decimal:
        normalized = (buffer_type or "fixed_amount").strip().lower()
        value = Decimal(str(buffer_value))

        if normalized == "fixed_amount":
            return _money(max(value, _ZERO))

        if normalized == "days_of_expenses":
            days = max(value, _ZERO)
            daily = max(Decimal(str(avg_daily_expense)), _ZERO)
            return _money(days * daily)

        # percentage_of_monthly_expenses reserved; V1 falls back to zero.
        if normalized == "percentage_of_monthly_expenses":
            monthly = max(Decimal(str(avg_daily_expense)), _ZERO) * Decimal("30")
            return _money(monthly * value / Decimal("100"))

        return _ZERO


def _money(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)
