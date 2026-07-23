"""Supported currency codes."""

from __future__ import annotations

from wealthos.shared.domain.exceptions import InvalidCurrency

ALLOWED_CURRENCIES = frozenset({"MXN", "USD", "EUR"})


class Currency:
    """ISO-like currency code constrained to WealthOS-supported set."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        code = value.strip().upper()
        if code not in ALLOWED_CURRENCIES:
            raise InvalidCurrency(
                f"Unsupported currency '{value}'. Allowed: {sorted(ALLOWED_CURRENCIES)}."
            )
        self._value = code

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Currency({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Currency):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
