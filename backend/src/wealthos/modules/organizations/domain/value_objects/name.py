"""Organization display name value object."""

from __future__ import annotations

from wealthos.modules.organizations.domain.exceptions import (
    OrganizationNameEmpty,
    OrganizationNameTooLong,
)

MAX_NAME_LENGTH = 100


class Name:
    """Human-readable organization name."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip()
        if not cleaned:
            raise OrganizationNameEmpty("Organization name cannot be empty.")
        if len(cleaned) > MAX_NAME_LENGTH:
            raise OrganizationNameTooLong(
                f"Organization name cannot exceed {MAX_NAME_LENGTH} characters."
            )
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Name({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Name):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
