"""Mexico expense treatment value object."""

from __future__ import annotations

from wealthos.modules.tax_mx.domain.exceptions import InvalidMexicoExpenseTreatment

ALLOWED = frozenset(
    {
        "deductible",
        "non_deductible",
        "partially_deductible",
        "investment",
        "cost_of_sales",
        "ignored",
    }
)


class MexicoExpenseTreatment:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            raise InvalidMexicoExpenseTreatment(f"Unsupported expense treatment: {value!r}")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MexicoExpenseTreatment):
            return NotImplemented
        return self._value == other._value

    def __repr__(self) -> str:
        return f"MexicoExpenseTreatment({self._value!r})"
