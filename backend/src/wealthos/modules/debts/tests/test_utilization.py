"""Utilization percentage helper tests."""

from decimal import Decimal

from wealthos.modules.debts.application.views.debt_view import utilization_percentage


def test_utilization_none_without_limit() -> None:
    assert utilization_percentage(owed_balance=Decimal("1000"), credit_limit=None) is None


def test_utilization_zero_when_settled() -> None:
    assert utilization_percentage(
        owed_balance=Decimal("0"),
        credit_limit=Decimal("50000"),
    ) == Decimal("0.00")


def test_utilization_allows_over_100() -> None:
    assert utilization_percentage(
        owed_balance=Decimal("60000"),
        credit_limit=Decimal("50000"),
    ) == Decimal("120.00")
