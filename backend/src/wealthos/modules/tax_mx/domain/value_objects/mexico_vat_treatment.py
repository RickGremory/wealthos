"""Mexico VAT treatment value object."""

from __future__ import annotations

from wealthos.modules.tax_mx.domain.exceptions import InvalidMexicoVATTreatment

ALLOWED = frozenset({"taxable", "zero_rate", "exempt", "not_subject", "not_identified"})


class MexicoVATTreatment:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            raise InvalidMexicoVATTreatment(f"Unsupported VAT treatment: {value!r}")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MexicoVATTreatment):
            return NotImplemented
        return self._value == other._value

    def __repr__(self) -> str:
        return f"MexicoVATTreatment({self._value!r})"
