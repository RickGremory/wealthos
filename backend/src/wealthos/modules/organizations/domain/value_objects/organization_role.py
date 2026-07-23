"""Organization membership role value object."""

from __future__ import annotations

from wealthos.modules.organizations.domain.exceptions import InvalidOrganizationRole

ALLOWED_ROLES = frozenset({"owner", "admin", "member", "viewer"})


class OrganizationRole:
    """Access role within an organization."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_ROLES:
            allowed = ", ".join(sorted(ALLOWED_ROLES))
            raise InvalidOrganizationRole(f"Role must be one of: {allowed}.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"OrganizationRole({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrganizationRole):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
