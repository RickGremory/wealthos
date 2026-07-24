"""Cash-flow granularity."""

from __future__ import annotations

from wealthos.modules.dashboard.domain.exceptions import InvalidCashFlowGranularity

ALLOWED = frozenset({"day", "week", "month"})


class CashFlowGranularity:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidCashFlowGranularity(f"Granularity must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CashFlowGranularity):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
