"""Category grouping mode for spending reports."""

from __future__ import annotations

from wealthos.modules.dashboard.domain.exceptions import InvalidCategoryGrouping

ALLOWED = frozenset({"root", "category"})


class CategoryGrouping:
    __slots__ = ("_value",)

    def __init__(self, value: str = "root") -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED:
            allowed = ", ".join(sorted(ALLOWED))
            raise InvalidCategoryGrouping(f"group_by must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_root(self) -> bool:
        return self._value == "root"

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CategoryGrouping):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
