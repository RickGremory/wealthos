"""Safety reserve strategies and reservation kinds (SPEC-004 §5)."""

from __future__ import annotations

from enum import StrEnum

from wealthos.modules.planning.domain.exceptions import InvalidSafetyReserveStrategy


class SafetyReserveStrategy(StrEnum):
    NONE = "none"
    FIXED_AMOUNT = "fixed_amount"
    LINKED_GOAL = "linked_goal"
    # Accepted by the contract but treated as ``none`` + alert until implemented.
    PERCENTAGE_OF_CASH = "percentage_of_cash"
    DAYS_OF_EXPENSES = "days_of_expenses"

    @classmethod
    def parse(cls, value: str | SafetyReserveStrategy) -> SafetyReserveStrategy:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            allowed = ", ".join(member.value for member in cls)
            raise InvalidSafetyReserveStrategy(f"Strategy must be one of: {allowed}.") from exc

    @property
    def is_supported(self) -> bool:
        return self in {
            SafetyReserveStrategy.NONE,
            SafetyReserveStrategy.FIXED_AMOUNT,
            SafetyReserveStrategy.LINKED_GOAL,
        }


class ReservationType(StrEnum):
    TAX = "tax"
    GOAL = "goal"
    SAFETY = "safety"
    LEGAL = "legal"
    MANUAL = "manual"
