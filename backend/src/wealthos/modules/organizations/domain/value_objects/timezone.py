"""IANA timezone value object."""

from __future__ import annotations

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from wealthos.modules.organizations.domain.exceptions import InvalidTimezone


class Timezone:
    """Valid IANA timezone identifier (e.g. America/Mexico_City)."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip()
        try:
            ZoneInfo(cleaned)
        except (ZoneInfoNotFoundError, KeyError, ValueError) as exc:
            raise InvalidTimezone(f"Invalid timezone '{value}'.") from exc
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Timezone({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Timezone):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
