"""Central money quantization for Planning (2 dp for MXN/USD/EUR today)."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def quantize_money(value: Decimal | str | int) -> Decimal:
    """Never accept float: Planning math is Decimal end to end."""
    if isinstance(value, float):  # noqa: UP038 — explicit runtime guard
        raise TypeError("Planning money does not accept float; use str or Decimal.")
    amount = value if isinstance(value, Decimal) else Decimal(str(value))
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def money_to_string(value: Decimal | None) -> str | None:
    """API representation — money crosses the wire as a string."""
    if value is None:
        return None
    return format(quantize_money(value), "f")
