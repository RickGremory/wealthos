"""Membership status value object."""

from __future__ import annotations

from wealthos.modules.organizations.domain.exceptions import InvalidMembershipStatus

ALLOWED_STATUSES = frozenset({"active", "invited", "suspended"})


class MembershipStatus:
    """Lifecycle status of an organization membership."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_STATUSES:
            allowed = ", ".join(sorted(ALLOWED_STATUSES))
            raise InvalidMembershipStatus(f"Status must be one of: {allowed}.")
        self._value = cleaned

    @classmethod
    def active(cls) -> MembershipStatus:
        return cls("active")

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"MembershipStatus({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MembershipStatus):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
