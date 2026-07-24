"""DebtPayment entity domain tests."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from wealthos.modules.debts.domain.entities.debt_payment import DebtPayment
from wealthos.modules.debts.domain.exceptions import (
    DebtPaymentAmountInvalid,
    DebtPaymentBreakdownInvalid,
)
from wealthos.shared.domain.value_objects.money import Money


def _make_payment(**overrides) -> DebtPayment:
    defaults = {
        "organization_id": uuid4(),
        "debt_id": uuid4(),
        "transaction_id": uuid4(),
        "amount": Money(Decimal("500.00"), "MXN"),
        "paid_at": datetime.now(UTC),
        "created_by_user_id": uuid4(),
    }
    defaults.update(overrides)
    return DebtPayment.create(**defaults)


def test_create_valid_payment() -> None:
    payment = _make_payment()
    assert payment.amount.amount == Decimal("500.00")
    assert payment.principal_amount is None
    assert payment.interest_amount is None


def test_rejects_non_positive_amount() -> None:
    with pytest.raises(DebtPaymentAmountInvalid):
        _make_payment(amount=Money(Decimal("0.00"), "MXN"))


def test_requires_both_principal_and_interest_or_neither() -> None:
    with pytest.raises(DebtPaymentBreakdownInvalid):
        _make_payment(principal_amount=Money(Decimal("400.00"), "MXN"))
    with pytest.raises(DebtPaymentBreakdownInvalid):
        _make_payment(interest_amount=Money(Decimal("100.00"), "MXN"))


def test_rejects_breakdown_currency_mismatch() -> None:
    with pytest.raises(DebtPaymentBreakdownInvalid):
        _make_payment(
            principal_amount=Money(Decimal("400.00"), "USD"),
            interest_amount=Money(Decimal("100.00"), "MXN"),
        )


def test_rejects_negative_breakdown_amounts() -> None:
    with pytest.raises(DebtPaymentBreakdownInvalid):
        _make_payment(
            principal_amount=Money(Decimal("-1.00"), "MXN"),
            interest_amount=Money(Decimal("501.00"), "MXN"),
        )


def test_rejects_breakdown_that_does_not_sum_to_amount() -> None:
    with pytest.raises(DebtPaymentBreakdownInvalid):
        _make_payment(
            principal_amount=Money(Decimal("300.00"), "MXN"),
            interest_amount=Money(Decimal("100.00"), "MXN"),
        )


def test_accepts_valid_breakdown() -> None:
    payment = _make_payment(
        principal_amount=Money(Decimal("400.00"), "MXN"),
        interest_amount=Money(Decimal("100.00"), "MXN"),
    )
    assert payment.principal_amount.amount == Decimal("400.00")
    assert payment.interest_amount.amount == Decimal("100.00")
