"""Budget forecast method value object."""

from __future__ import annotations

from wealthos.modules.planning.domain.exceptions import InvalidForecastMethod

ALLOWED = frozenset({"linear", "scheduled", "manual"})


class ForecastMethod:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidForecastMethod(f"Forecast method must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"ForecastMethod({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ForecastMethod):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
