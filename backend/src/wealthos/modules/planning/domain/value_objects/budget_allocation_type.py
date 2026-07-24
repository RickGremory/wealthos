"""Budget allocation type value object."""

from __future__ import annotations

from wealthos.modules.planning.domain.exceptions import InvalidBudgetAllocationType

ALLOWED = frozenset(
    {
        "income",
        "expense",
        "savings",
        "tax_reserve",
        "debt_payment",
        "goal_contribution",
        "unallocated",
    }
)


class BudgetAllocationType:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidBudgetAllocationType(f"Budget allocation type must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def requires_category(self) -> bool:
        return self._value in {"income", "expense"}

    @property
    def requires_goal(self) -> bool:
        return self._value == "goal_contribution"

    @property
    def requires_debt(self) -> bool:
        return self._value == "debt_payment"

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"BudgetAllocationType({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BudgetAllocationType):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
