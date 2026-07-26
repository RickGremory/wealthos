"""Annual interest rate as a percentage Decimal (never float).

Convention (SPEC-002): 42.5% is stored as 42.500000 — never 0.425.
Precision: Numeric(9, 6) / six decimal places.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from wealthos.modules.debts.domain.exceptions import InvalidInterestRate

_SIX_PLACES = Decimal("0.000001")


class InterestRate:
    """Stored as annual percentage, e.g. 42.500000 means 42.5% APR."""

    __slots__ = ("_annual_percentage",)

    def __init__(self, annual_percentage: Decimal | str | int) -> None:
        if isinstance(annual_percentage, float):
            raise TypeError("InterestRate does not accept float; use str or Decimal.")
        value = (
            annual_percentage
            if isinstance(annual_percentage, Decimal)
            else Decimal(str(annual_percentage))
        )
        if value < 0:
            raise InvalidInterestRate("Interest rate cannot be negative.")
        self._annual_percentage = value.quantize(_SIX_PLACES, rounding=ROUND_HALF_UP)

    @property
    def annual_percentage(self) -> Decimal:
        return self._annual_percentage

    @property
    def monthly_rate(self) -> Decimal:
        """Fractional monthly rate: annual% / 12 / 100."""
        return (self._annual_percentage / Decimal("1200")).quantize(
            Decimal("0.00000001"),
            rounding=ROUND_HALF_UP,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InterestRate):
            return NotImplemented
        return self._annual_percentage == other._annual_percentage

    def __repr__(self) -> str:
        return f"InterestRate({self._annual_percentage!r})"

    def __str__(self) -> str:
        return f"{self._annual_percentage}%"
