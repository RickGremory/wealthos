"""Category name value object with display + normalized forms."""

from __future__ import annotations

import re
import unicodedata

from wealthos.modules.categories.domain.exceptions import (
    CategoryNameEmpty,
    CategoryNameTooLong,
)

MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 80
_MULTI_SPACE = re.compile(r"\s+")


def normalize_category_name(value: str) -> str:
    """Lowercase, collapse spaces, and strip accents for uniqueness checks."""
    cleaned = _MULTI_SPACE.sub(" ", value.strip()).lower()
    decomposed = unicodedata.normalize("NFKD", cleaned)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


class CategoryName:
    """Display name for a category (preserves accents/case for UI)."""

    __slots__ = ("_value", "_normalized")

    def __init__(self, value: str) -> None:
        cleaned = _MULTI_SPACE.sub(" ", value.strip())
        if len(cleaned) < MIN_NAME_LENGTH:
            raise CategoryNameEmpty(f"Category name must be at least {MIN_NAME_LENGTH} characters.")
        if len(cleaned) > MAX_NAME_LENGTH:
            raise CategoryNameTooLong(f"Category name cannot exceed {MAX_NAME_LENGTH} characters.")
        self._value = cleaned
        self._normalized = normalize_category_name(cleaned)

    @property
    def value(self) -> str:
        return self._value

    @property
    def normalized(self) -> str:
        return self._normalized

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"CategoryName({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CategoryName):
            return NotImplemented
        return self._normalized == other._normalized

    def __hash__(self) -> int:
        return hash(self._normalized)
