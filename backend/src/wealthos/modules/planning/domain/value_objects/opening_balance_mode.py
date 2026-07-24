"""Opening balance mode value object."""

from __future__ import annotations

from wealthos.modules.planning.domain.exceptions import InvalidOpeningBalanceMode

ALLOWED = frozenset({"current_liquid_balance", "selected_accounts", "manual"})


class OpeningBalanceMode:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidOpeningBalanceMode(f"Opening balance mode must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_manual(self) -> bool:
        return self._value == "manual"

    @property
    def is_selected_accounts(self) -> bool:
        return self._value == "selected_accounts"

    @property
    def is_current_liquid_balance(self) -> bool:
        return self._value == "current_liquid_balance"

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"OpeningBalanceMode({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OpeningBalanceMode):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
