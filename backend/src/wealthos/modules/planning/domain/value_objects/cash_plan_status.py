"""Cash plan lifecycle status value object."""

from __future__ import annotations

from wealthos.modules.planning.domain.exceptions import InvalidCashPlanStatus

ALLOWED = frozenset({"draft", "active", "completed", "archived"})


class CashPlanStatus:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidCashPlanStatus(f"Cash plan status must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_draft(self) -> bool:
        return self._value == "draft"

    @property
    def is_active(self) -> bool:
        return self._value == "active"

    @property
    def is_completed(self) -> bool:
        return self._value == "completed"

    @property
    def is_archived(self) -> bool:
        return self._value == "archived"

    @property
    def is_editable(self) -> bool:
        return self._value in {"draft", "active"}

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"CashPlanStatus({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CashPlanStatus):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
