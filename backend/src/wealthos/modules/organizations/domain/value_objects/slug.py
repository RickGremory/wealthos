"""URL-safe organization slug value object."""

from __future__ import annotations

import re

from wealthos.modules.organizations.domain.exceptions import OrganizationSlugInvalid

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_SLUG_LENGTH = 80


class OrganizationSlug:
    """Kebab-case identifier used in URLs and lookups."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if not cleaned or not _SLUG_PATTERN.fullmatch(cleaned):
            raise OrganizationSlugInvalid(
                "Slug must be lowercase kebab-case (e.g. ricardo-personal)."
            )
        if len(cleaned) > MAX_SLUG_LENGTH:
            raise OrganizationSlugInvalid(f"Slug cannot exceed {MAX_SLUG_LENGTH} characters.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"OrganizationSlug({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrganizationSlug):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
