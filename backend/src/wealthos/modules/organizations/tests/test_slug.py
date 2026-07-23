import pytest

from wealthos.modules.organizations.domain.exceptions import OrganizationSlugInvalid
from wealthos.modules.organizations.domain.value_objects.slug import Slug


def test_slug_accepts_kebab_case() -> None:
    assert Slug("ricardo-personal").value == "ricardo-personal"


def test_slug_normalizes_case() -> None:
    assert Slug("Ricardo-Personal").value == "ricardo-personal"


def test_slug_rejects_spaces() -> None:
    with pytest.raises(OrganizationSlugInvalid):
        Slug("ricardo personal")


def test_slug_rejects_underscores() -> None:
    with pytest.raises(OrganizationSlugInvalid):
        Slug("ricardo_personal")
