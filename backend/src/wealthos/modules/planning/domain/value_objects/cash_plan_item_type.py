"""Cash plan item type value object."""

from __future__ import annotations

from wealthos.modules.planning.domain.exceptions import InvalidCashPlanItemType

ALLOWED = frozenset({"inflow", "outflow", "transfer_in", "transfer_out"})


class CashPlanItemType:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidCashPlanItemType(f"Cash plan item type must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_inflow(self) -> bool:
        return self._value in {"inflow", "transfer_in"}

    @property
    def is_outflow(self) -> bool:
        return self._value in {"outflow", "transfer_out"}

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"CashPlanItemType({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CashPlanItemType):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
