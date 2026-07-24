"""Tax base type value object."""

from __future__ import annotations

from wealthos.modules.taxes.domain.exceptions import InvalidTaxBaseType

ALLOWED = frozenset(
    {
        "gross_income",
        "net_income",
        "expenses",
        "category_income",
        "category_expense",
        "transaction_amount",
    }
)


class TaxBaseType:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidTaxBaseType(f"TaxBaseType must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"TaxBaseType({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaxBaseType):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
