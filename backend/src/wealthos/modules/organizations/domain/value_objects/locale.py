"""Locale value object (language_REGION)."""

from __future__ import annotations

import re

from wealthos.modules.organizations.domain.exceptions import InvalidLocale

_LOCALE_PATTERN = re.compile(r"^[a-z]{2}_[A-Z]{2}$")


class Locale:
    """Simple locale tag such as es_MX or en_US."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip()
        if not _LOCALE_PATTERN.fullmatch(cleaned):
            raise InvalidLocale("Locale must match language_REGION (e.g. es_MX, en_US).")
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
