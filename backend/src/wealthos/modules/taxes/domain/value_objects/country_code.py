"""ISO-3166 alpha-2 country code."""

from __future__ import annotations

import re

from wealthos.modules.taxes.domain.exceptions import InvalidCountryCode

_PATTERN = re.compile(r"^[A-Z]{2}$")


class CountryCode:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().upper()
        if not _PATTERN.fullmatch(cleaned):
            raise InvalidCountryCode("Country code must be a 2-letter ISO code.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"CountryCode({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CountryCode):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
