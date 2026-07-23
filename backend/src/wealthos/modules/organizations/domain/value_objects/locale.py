"""Locale value object (language-REGION)."""

from __future__ import annotations

import re

from wealthos.modules.organizations.domain.exceptions import InvalidLocale

_LOCALE_PATTERN = re.compile(r"^[a-z]{2}-[A-Z]{2}$")


class Locale:
    """BCP 47-style locale tag such as es-MX or en-US."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip()
        if not _LOCALE_PATTERN.fullmatch(cleaned):
            raise InvalidLocale("Locale must match language-REGION (e.g. es-MX, en-US).")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Locale({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Locale):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
