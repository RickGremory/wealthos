import pytest

from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.exceptions import InvalidCurrency
from wealthos.modules.organizations.domain.value_objects.currency import Currency
from wealthos.modules.organizations.domain.value_objects.name import Name


def test_organization_create_factory() -> None:
    org = Organization.create(
        name="Ricardo Personal",
        slug="ricardo-personal",
    )
    assert org.name.value == "Ricardo Personal"
    assert org.slug.value == "ricardo-personal"
    assert org.currency.value == "MXN"
    assert org.timezone.value == "America/Mexico_City"
    assert org.locale.value == "es_MX"


def test_organization_rename() -> None:
    org = Organization.create(name="Old", slug="old")
    org.rename("Tecnicora")
    assert org.name == Name("Tecnicora")


def test_organization_change_currency() -> None:
    org = Organization.create(name="Personal", slug="personal")
    org.change_currency("USD")
    assert org.currency == Currency("USD")


def test_organization_change_currency_rejects_invalid() -> None:
    org = Organization.create(name="Personal", slug="personal")
    with pytest.raises(InvalidCurrency):
        org.change_currency("BTC")
