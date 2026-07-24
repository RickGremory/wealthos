"""Alert type value object."""

from __future__ import annotations

from wealthos.modules.planning.domain.exceptions import PlanningError

ALLOWED = frozenset(
    {
        "cash_shortfall",
        "low_cash_buffer",
        "overdue_inflow",
        "large_outflow",
        "tax_reserve_shortfall",
        "debt_payment_at_risk",
        "budget_overspend",
        "goal_contribution_at_risk",
    }
)


class AlertType:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise PlanningError(f"Alert type must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"AlertType({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AlertType):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
