import pytest

from wealthos.modules.organizations.domain.exceptions import OrganizationSlugInvalid
from wealthos.modules.organizations.domain.value_objects.slug import OrganizationSlug


def test_slug_accepts_kebab_case() -> None:
    assert OrganizationSlug("ricardo-personal").value == "ricardo-personal"


def test_slug_normalizes_case() -> None:
    assert OrganizationSlug("Ricardo-Personal").value == "ricardo-personal"


def test_slug_rejects_spaces() -> None:
    with pytest.raises(OrganizationSlugInvalid):
        OrganizationSlug("ricardo personal")


def test_slug_rejects_underscores() -> None:
    with pytest.raises(OrganizationSlugInvalid):
        OrganizationSlug("ricardo_personal")
