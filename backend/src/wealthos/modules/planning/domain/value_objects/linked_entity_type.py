"""Linked entity type value object for cash plan items."""

from __future__ import annotations

from wealthos.modules.planning.domain.exceptions import InvalidLinkedEntityType

ALLOWED = frozenset({"debt", "tax_period", "goal", "transaction", "invoice", "manual"})


class LinkedEntityType:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidLinkedEntityType(f"Linked entity type must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"LinkedEntityType({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LinkedEntityType):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
