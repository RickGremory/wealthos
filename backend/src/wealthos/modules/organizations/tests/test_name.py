import pytest

from wealthos.modules.organizations.domain.exceptions import (
    OrganizationNameEmpty,
    OrganizationNameTooLong,
)
from wealthos.modules.organizations.domain.value_objects.name import Name


def test_name_accepts_valid_value() -> None:
    assert Name("Ricardo Personal").value == "Ricardo Personal"


def test_name_strips_whitespace() -> None:
    assert Name("  Tecnicora  ").value == "Tecnicora"


def test_name_rejects_empty() -> None:
    with pytest.raises(OrganizationNameEmpty):
        Name("   ")


def test_name_rejects_too_long() -> None:
    with pytest.raises(OrganizationNameTooLong):
        Name("x" * 101)
