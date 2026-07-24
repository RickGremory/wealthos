"""Goal status value object."""

from __future__ import annotations

from wealthos.modules.goals.domain.exceptions import InvalidGoalStatus

ALLOWED = frozenset({"active", "completed", "archived"})


class GoalStatus:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidGoalStatus(f"Goal status must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_active(self) -> bool:
        return self._value == "active"

    @property
    def is_completed(self) -> bool:
        return self._value == "completed"

    @property
    def is_archived(self) -> bool:
        return self._value == "archived"

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"GoalStatus({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GoalStatus):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
