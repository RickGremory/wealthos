"""Budget rollover amount from planned vs actual under policy."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

_ZERO = Decimal("0.00")
_CENT = Decimal("0.01")


class BudgetRolloverService:
    """Compute rollover amount for none | positive_only | full policies."""

    def calculate(
        self,
        *,
        planned: Decimal,
        actual: Decimal,
        policy: str,
    ) -> Decimal:
        unused = Decimal(str(planned)) - Decimal(str(actual))
        normalized = (policy or "none").strip().lower()

        if normalized == "none":
            return _ZERO
        if normalized == "positive_only":
            return _money(unused) if unused > _ZERO else _ZERO
        if normalized == "full":
            return _money(unused)
        return _ZERO


def _money(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)
