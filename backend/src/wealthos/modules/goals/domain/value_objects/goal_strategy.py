"""Goal progress strategy value object."""

from __future__ import annotations

from wealthos.modules.goals.domain.exceptions import InvalidGoalStrategy

ALLOWED = frozenset({"manual", "linked_accounts", "net_worth_percentage"})


class GoalStrategy:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidGoalStrategy(f"Goal strategy must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_manual(self) -> bool:
        return self._value == "manual"

    @property
    def is_linked_accounts(self) -> bool:
        return self._value == "linked_accounts"

    @property
    def is_net_worth_percentage(self) -> bool:
        return self._value == "net_worth_percentage"

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"GoalStrategy({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GoalStrategy):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
