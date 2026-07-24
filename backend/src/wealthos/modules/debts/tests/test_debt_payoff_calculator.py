"""DebtPayoffCalculator projection tests."""

from datetime import date
from decimal import Decimal

from wealthos.modules.debts.application.services.debt_payoff_calculator import (
    DebtPayoffCalculator,
    DebtPayoffInput,
)

_START = date(2026, 1, 1)


def test_zero_balance_is_already_paid_off() -> None:
    calculator = DebtPayoffCalculator()
    result = calculator.project(
        DebtPayoffInput(
            balance=Decimal("0.00"),
            annual_interest_rate=Decimal("20"),
            monthly_payment=Decimal("100.00"),
        ),
        start_date=_START,
    )
    assert result.is_payment_sufficient
    assert result.months_remaining == 0
    assert result.total_interest == Decimal("0.00")


def test_zero_interest_rate_divides_evenly() -> None:
    calculator = DebtPayoffCalculator()
    result = calculator.project(
        DebtPayoffInput(
            balance=Decimal("1200.00"),
            annual_interest_rate=Decimal("0"),
            monthly_payment=Decimal("100.00"),
        ),
        start_date=_START,
    )
    assert result.is_payment_sufficient
    assert result.months_remaining == 12
    assert result.total_interest == Decimal("0.00")
    assert result.total_paid == Decimal("1200.00")
    assert result.payoff_date == date(2027, 1, 1)


def test_accrues_interest_and_reduces_principal() -> None:
    calculator = DebtPayoffCalculator()
    result = calculator.project(
        DebtPayoffInput(
            balance=Decimal("1000.00"),
            annual_interest_rate=Decimal("12"),
            monthly_payment=Decimal("100.00"),
        ),
        start_date=_START,
    )
    assert result.is_payment_sufficient
    assert result.total_interest is not None
    assert result.total_interest > Decimal("0.00")
    # Interest accrues, so total paid exceeds the original balance.
    assert result.total_paid > Decimal("1000.00")
    assert result.months_remaining is not None
    assert result.months_remaining >= 10


def test_insufficient_payment_below_monthly_interest() -> None:
    calculator = DebtPayoffCalculator()
    result = calculator.project(
        DebtPayoffInput(
            balance=Decimal("10000.00"),
            annual_interest_rate=Decimal("42"),
            monthly_payment=Decimal("50.00"),
        ),
        start_date=_START,
    )
    assert result.is_payment_sufficient is False
    assert result.payoff_date is None
    assert result.months_remaining is None
    assert result.total_interest is None
    assert result.total_paid is None


def test_insufficient_when_payment_is_zero() -> None:
    calculator = DebtPayoffCalculator()
    result = calculator.project(
        DebtPayoffInput(
            balance=Decimal("500.00"),
            annual_interest_rate=Decimal("10"),
            monthly_payment=Decimal("0.00"),
        ),
        start_date=_START,
    )
    assert result.is_payment_sufficient is False


def test_extra_monthly_payment_reduces_months_remaining() -> None:
    calculator = DebtPayoffCalculator()
    base = calculator.project(
        DebtPayoffInput(
            balance=Decimal("5000.00"),
            annual_interest_rate=Decimal("24"),
            monthly_payment=Decimal("200.00"),
        ),
        start_date=_START,
    )
    with_extra = calculator.project(
        DebtPayoffInput(
            balance=Decimal("5000.00"),
            annual_interest_rate=Decimal("24"),
            monthly_payment=Decimal("200.00"),
            extra_monthly_payment=Decimal("200.00"),
        ),
        start_date=_START,
    )
    assert base.is_payment_sufficient
    assert with_extra.is_payment_sufficient
    assert with_extra.months_remaining < base.months_remaining
    assert with_extra.total_interest < base.total_interest


def test_very_high_interest_rate_above_100_percent() -> None:
    calculator = DebtPayoffCalculator()
    result = calculator.project(
        DebtPayoffInput(
            balance=Decimal("1000.00"),
            annual_interest_rate=Decimal("350"),
            monthly_payment=Decimal("500.00"),
        ),
        start_date=_START,
    )
    # 350% APR => ~29.17% monthly; a 500 payment on 1000 balance is still sufficient.
    assert result.is_payment_sufficient
    assert result.total_interest is not None
    assert result.total_interest > Decimal("0.00")


def test_very_high_interest_rate_insufficient_with_small_payment() -> None:
    calculator = DebtPayoffCalculator()
    result = calculator.project(
        DebtPayoffInput(
            balance=Decimal("1000.00"),
            annual_interest_rate=Decimal("350"),
            monthly_payment=Decimal("100.00"),
        ),
        start_date=_START,
    )
    # Monthly interest (~291.67) exceeds the payment, so principal never reduces.
    assert result.is_payment_sufficient is False
