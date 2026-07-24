"""Tax period type value object."""

from __future__ import annotations

from wealthos.modules.taxes.domain.exceptions import InvalidTaxPeriod

ALLOWED = frozenset({"monthly", "quarterly", "annual"})


class TaxPeriodType:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidTaxPeriod(f"TaxPeriodType must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"TaxPeriodType({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaxPeriodType):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
