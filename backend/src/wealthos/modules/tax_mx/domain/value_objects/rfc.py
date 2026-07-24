"""Mexican RFC structural value object."""

from __future__ import annotations

import re

from wealthos.modules.tax_mx.domain.exceptions import InvalidRFC

# Persona física: 4 letters + 6 digits + 3 alnum; moral: 3 letters + 6 digits + 3 alnum.
_PATTERN = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")


class RFC:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().upper().replace(" ", "")
        if not _PATTERN.fullmatch(cleaned):
            raise InvalidRFC("RFC structure is invalid.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"RFC({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RFC):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
