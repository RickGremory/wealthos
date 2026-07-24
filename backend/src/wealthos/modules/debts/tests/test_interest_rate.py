"""InterestRate value object tests."""

from decimal import Decimal

import pytest

from wealthos.modules.debts.domain.exceptions import InvalidInterestRate
from wealthos.modules.debts.domain.value_objects.interest_rate import InterestRate


def test_stores_annual_percentage_rounded_to_four_places() -> None:
    rate = InterestRate("42.12345")
    assert rate.annual_percentage == Decimal("42.1235")


def test_accepts_int_and_decimal() -> None:
    assert InterestRate(0).annual_percentage == Decimal("0.0000")
    assert InterestRate(Decimal("18.5")).annual_percentage == Decimal("18.5000")


def test_rejects_float() -> None:
    with pytest.raises(TypeError):
        InterestRate(18.5)  # type: ignore[arg-type]


def test_rejects_negative_rate() -> None:
    with pytest.raises(InvalidInterestRate):
        InterestRate("-1")


def test_monthly_rate_is_annual_divided_by_1200() -> None:
    rate = InterestRate("24")
    assert rate.monthly_rate == Decimal("0.02000000")


def test_equality_and_repr() -> None:
    a = InterestRate("10")
    b = InterestRate("10.00")
    c = InterestRate("10.01")
    assert a == b
    assert a != c
    assert "InterestRate" in repr(a)
    assert str(a) == "10.0000%"
