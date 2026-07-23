"""Slug helpers for organization creation during registration."""

from __future__ import annotations

import re
import unicodedata

from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationRepository,
)
from wealthos.modules.organizations.domain.value_objects.slug import OrganizationSlug

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def slugify_organization_name(name: str) -> str:
    """Convert a display name into a kebab-case slug base."""
    normalized = unicodedata.normalize("NFKD", name)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = _NON_ALNUM.sub("-", ascii_text.lower()).strip("-")
    return cleaned or "organization"


def allocate_unique_slug(
    repository: OrganizationRepository,
    organization_name: str,
) -> str:
    """Return a unique slug derived from the organization name."""
    base = slugify_organization_name(organization_name)
    candidate = base
    suffix = 2
    while repository.get_by_slug(OrganizationSlug(candidate)) is not None:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate
