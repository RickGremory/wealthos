"""Annual interest rate as a percentage Decimal (never float)."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from wealthos.modules.debts.domain.exceptions import InvalidInterestRate

_FOUR_PLACES = Decimal("0.0001")


class InterestRate:
    """Stored as annual percentage, e.g. 42.50 means 42.50% APR."""

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
        self._annual_percentage = value.quantize(_FOUR_PLACES, rounding=ROUND_HALF_UP)

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
