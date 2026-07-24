"""Debt type value object (contract kind, distinct from AccountType)."""

from __future__ import annotations

from wealthos.modules.debts.domain.exceptions import InvalidDebtType

ALLOWED = frozenset(
    {
        "credit_card",
        "personal_loan",
        "auto_loan",
        "mortgage",
        "student_loan",
        "tax_debt",
        "line_of_credit",
        "other",
    }
)


class DebtType:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidDebtType(f"Debt type must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"DebtType({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DebtType):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
