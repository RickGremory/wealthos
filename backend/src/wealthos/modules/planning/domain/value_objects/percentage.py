"""Percentage value object constrained to 0–100 (never float)."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from wealthos.modules.planning.domain.exceptions import InvalidPercentage

_FOUR = Decimal("0.0001")
_MAX = Decimal("100")


class Percentage:
    __slots__ = ("_value",)

    def __init__(self, value: Decimal | str | int) -> None:
        if isinstance(value, float):
            raise TypeError("Percentage does not accept float.")
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
        if amount < 0:
            raise InvalidPercentage("Percentage cannot be negative.")
        if amount > _MAX:
            raise InvalidPercentage(f"Percentage cannot exceed {_MAX}.")
        self._value = amount.quantize(_FOUR, rounding=ROUND_HALF_UP)

    @property
    def value(self) -> Decimal:
        return self._value

    def as_fraction(self) -> Decimal:
        return (self._value / Decimal("100")).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Percentage):
            return NotImplemented
        return self._value == other._value

    def __repr__(self) -> str:
        return f"Percentage({self._value!r})"

    def __str__(self) -> str:
        return f"{self._value}%"
