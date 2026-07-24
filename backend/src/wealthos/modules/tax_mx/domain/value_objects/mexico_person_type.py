"""Mexico person type value object."""

from __future__ import annotations

from wealthos.modules.tax_mx.domain.exceptions import InvalidMexicoPersonType

ALLOWED = frozenset({"individual", "legal_entity"})


class MexicoPersonType:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            raise InvalidMexicoPersonType(f"Unsupported person type: {value!r}")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def to_taxpayer_type(self) -> str:
        return "individual" if self._value == "individual" else "business"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MexicoPersonType):
            return NotImplemented
        return self._value == other._value

    def __repr__(self) -> str:
        return f"MexicoPersonType({self._value!r})"
