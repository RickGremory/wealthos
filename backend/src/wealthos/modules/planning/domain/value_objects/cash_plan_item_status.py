"""Cash plan item status value object."""

from __future__ import annotations

from wealthos.modules.planning.domain.exceptions import InvalidCashPlanItemStatus

ALLOWED = frozenset(
    {
        "planned",
        "confirmed",
        "partially_matched",
        "matched",
        "cancelled",
        "overdue",
    }
)


class CashPlanItemStatus:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidCashPlanItemStatus(f"Cash plan item status must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_planned(self) -> bool:
        return self._value == "planned"

    @property
    def is_confirmed(self) -> bool:
        return self._value == "confirmed"

    @property
    def is_partially_matched(self) -> bool:
        return self._value == "partially_matched"

    @property
    def is_matched(self) -> bool:
        return self._value == "matched"

    @property
    def is_cancelled(self) -> bool:
        return self._value == "cancelled"

    @property
    def is_overdue(self) -> bool:
        return self._value == "overdue"

    @property
    def is_matchable(self) -> bool:
        return self._value in {"planned", "confirmed", "partially_matched", "overdue"}

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"CashPlanItemStatus({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CashPlanItemStatus):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
