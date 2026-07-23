"""Account type value object."""

from __future__ import annotations

from wealthos.modules.accounts.domain.exceptions import InvalidAccountType

ASSET_TYPES = frozenset({"checking", "savings", "cash", "investment", "digital_wallet", "other"})
LIABILITY_TYPES = frozenset({"credit_card", "loan"})
ALLOWED_TYPES = ASSET_TYPES | LIABILITY_TYPES


class AccountType:
    """Classification of a financial account container."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_TYPES:
            allowed = ", ".join(sorted(ALLOWED_TYPES))
            raise InvalidAccountType(f"Account type must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_asset(self) -> bool:
        return self._value in ASSET_TYPES

    @property
    def is_liability(self) -> bool:
        return self._value in LIABILITY_TYPES

    @property
    def classification(self) -> str:
        return "liability" if self.is_liability else "asset"

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"AccountType({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccountType):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
