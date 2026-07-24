"""Goal name value object."""

from __future__ import annotations

import re

from wealthos.modules.goals.domain.exceptions import GoalNameEmpty, GoalNameTooLong

MIN_LENGTH = 2
MAX_LENGTH = 120
_MULTI_SPACE = re.compile(r"\s+")


class GoalName:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = _MULTI_SPACE.sub(" ", value.strip())
        if len(cleaned) < MIN_LENGTH:
            raise GoalNameEmpty(f"Goal name must be at least {MIN_LENGTH} characters.")
        if len(cleaned) > MAX_LENGTH:
            raise GoalNameTooLong(f"Goal name cannot exceed {MAX_LENGTH} characters.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"GoalName({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GoalName):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
