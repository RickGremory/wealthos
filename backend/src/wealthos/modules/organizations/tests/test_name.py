import pytest

from wealthos.modules.organizations.domain.exceptions import (
    OrganizationNameEmpty,
    OrganizationNameTooLong,
)
from wealthos.modules.organizations.domain.value_objects.name import OrganizationName


def test_name_accepts_valid() -> None:
    assert OrganizationName("Ricardo Personal").value == "Ricardo Personal"


def test_name_strips_whitespace() -> None:
    assert OrganizationName("  Tecnicora  ").value == "Tecnicora"


def test_name_rejects_empty() -> None:
    with pytest.raises(OrganizationNameEmpty):
        OrganizationName("   ")


def test_name_rejects_too_long() -> None:
    with pytest.raises(OrganizationNameTooLong):
        OrganizationName("x" * 121)
