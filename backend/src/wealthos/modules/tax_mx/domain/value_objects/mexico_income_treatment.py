"""Mexico income treatment value object."""

from __future__ import annotations

from wealthos.modules.tax_mx.domain.exceptions import InvalidMexicoIncomeTreatment

ALLOWED = frozenset({"taxable", "non_taxable", "exempt", "withheld", "ignored"})


class MexicoIncomeTreatment:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            raise InvalidMexicoIncomeTreatment(f"Unsupported income treatment: {value!r}")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MexicoIncomeTreatment):
            return NotImplemented
        return self._value == other._value

    def __repr__(self) -> str:
        return f"MexicoIncomeTreatment({self._value!r})"
