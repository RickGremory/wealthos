"""Account name value object."""

from __future__ import annotations

import re

from wealthos.modules.accounts.domain.exceptions import AccountNameEmpty, AccountNameTooLong

MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100
_MULTI_SPACE = re.compile(r"\s+")


class AccountName:
    """Human-readable account label within an organization."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = _MULTI_SPACE.sub(" ", value.strip())
        if len(cleaned) < MIN_NAME_LENGTH:
            raise AccountNameEmpty(f"Account name must be at least {MIN_NAME_LENGTH} characters.")
        if len(cleaned) > MAX_NAME_LENGTH:
            raise AccountNameTooLong(f"Account name cannot exceed {MAX_NAME_LENGTH} characters.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"AccountName({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccountName):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
