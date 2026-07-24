"""Transaction description value object."""

from __future__ import annotations

import re

from wealthos.modules.transactions.domain.exceptions import (
    TransactionDescriptionEmpty,
    TransactionDescriptionTooLong,
)

MIN_DESCRIPTION_LENGTH = 2
MAX_DESCRIPTION_LENGTH = 200
_MULTI_SPACE = re.compile(r"\s+")


class TransactionDescription:
    """Human-readable description for a transaction."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = _MULTI_SPACE.sub(" ", value.strip())
        if len(cleaned) < MIN_DESCRIPTION_LENGTH:
            raise TransactionDescriptionEmpty(
                f"Description must be at least {MIN_DESCRIPTION_LENGTH} characters."
            )
        if len(cleaned) > MAX_DESCRIPTION_LENGTH:
            raise TransactionDescriptionTooLong(
                f"Description cannot exceed {MAX_DESCRIPTION_LENGTH} characters."
            )
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"TransactionDescription({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TransactionDescription):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
