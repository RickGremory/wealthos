"""Money value object tests."""

from decimal import Decimal

import pytest

from wealthos.shared.domain.exceptions import CurrencyMismatch
from wealthos.shared.domain.value_objects.currency import Currency
from wealthos.shared.domain.value_objects.money import Money


def test_money_from_str_and_decimal() -> None:
    assert Money("15000.00", Currency("MXN")).amount == Decimal("15000.00")
    assert Money(Decimal("-3400.50"), "MXN").amount == Decimal("-3400.50")


def test_money_rejects_float() -> None:
    with pytest.raises(TypeError):
        Money(0.1 + 0.2, "MXN")  # type: ignore[arg-type]


def test_money_adds_same_currency() -> None:
    total = Money("10.00", "MXN") + Money("2.50", "MXN")
    assert total.amount == Decimal("12.50")


def test_money_rejects_currency_mismatch() -> None:
    with pytest.raises(CurrencyMismatch):
        _ = Money("10.00", "MXN") + Money("2.50", "USD")


def test_money_allows_negative() -> None:
    assert Money("-1.00", "MXN").amount < 0
