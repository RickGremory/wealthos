"""Dashboard period presets."""

from __future__ import annotations

from wealthos.modules.dashboard.domain.exceptions import InvalidDashboardPeriod

ALLOWED_PERIODS = frozenset({"this_month", "last_month", "last_30_days", "this_year", "custom"})


class DashboardPeriod:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_PERIODS:
            allowed = ", ".join(sorted(ALLOWED_PERIODS))
            raise InvalidDashboardPeriod(f"Period must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_custom(self) -> bool:
        return self._value == "custom"

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DashboardPeriod):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
