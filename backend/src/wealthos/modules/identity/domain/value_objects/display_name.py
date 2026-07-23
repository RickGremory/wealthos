"""Display name value object."""

from __future__ import annotations

from wealthos.modules.identity.domain.exceptions import DisplayNameEmpty, DisplayNameTooLong

MIN_DISPLAY_NAME_LENGTH = 2
MAX_DISPLAY_NAME_LENGTH = 100


class DisplayName:
    """Human-readable user display name."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip()
        if len(cleaned) < MIN_DISPLAY_NAME_LENGTH:
            raise DisplayNameEmpty(
                f"Display name must be at least {MIN_DISPLAY_NAME_LENGTH} characters."
            )
        if len(cleaned) > MAX_DISPLAY_NAME_LENGTH:
            raise DisplayNameTooLong(
                f"Display name cannot exceed {MAX_DISPLAY_NAME_LENGTH} characters."
            )
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"DisplayName({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DisplayName):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
