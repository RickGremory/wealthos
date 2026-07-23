import pytest

from wealthos.modules.organizations.domain.exceptions import InvalidCurrency
from wealthos.modules.organizations.domain.value_objects.currency import Currency


def test_currency_accepts_mxn() -> None:
    assert Currency("MXN").value == "MXN"


def test_currency_normalizes_lowercase() -> None:
    assert Currency("usd").value == "USD"


def test_currency_rejects_invalid_code() -> None:
    with pytest.raises(InvalidCurrency):
        Currency("BTC")
