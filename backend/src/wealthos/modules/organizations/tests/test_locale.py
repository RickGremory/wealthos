import pytest

from wealthos.modules.organizations.domain.exceptions import InvalidLocale
from wealthos.modules.organizations.domain.value_objects.locale import Locale


def test_locale_accepts_es_mx() -> None:
    assert Locale("es_MX").value == "es_MX"


def test_locale_rejects_invalid() -> None:
    with pytest.raises(InvalidLocale):
        Locale("es-mx")
