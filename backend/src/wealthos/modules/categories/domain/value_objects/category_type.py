"""Category type value object."""

from __future__ import annotations

from wealthos.modules.categories.domain.exceptions import InvalidCategoryType

ALLOWED_TYPES = frozenset({"income", "expense"})


class CategoryType:
    """Income or expense classification for a category."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_TYPES:
            allowed = ", ".join(sorted(ALLOWED_TYPES))
            raise InvalidCategoryType(f"Category type must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_income(self) -> bool:
        return self._value == "income"

    @property
    def is_expense(self) -> bool:
        return self._value == "expense"

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"CategoryType({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CategoryType):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
