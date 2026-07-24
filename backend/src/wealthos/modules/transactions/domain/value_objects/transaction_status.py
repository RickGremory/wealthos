"""Transaction status value object."""

from __future__ import annotations

from wealthos.modules.transactions.domain.exceptions import InvalidTransactionStatus

ALLOWED_STATUSES = frozenset({"posted", "voided"})


class TransactionStatus:
    """Lifecycle status of a transaction."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_STATUSES:
            allowed = ", ".join(sorted(ALLOWED_STATUSES))
            raise InvalidTransactionStatus(f"Transaction status must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_posted(self) -> bool:
        return self._value == "posted"

    @property
    def is_voided(self) -> bool:
        return self._value == "voided"

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"TransactionStatus({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TransactionStatus):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
