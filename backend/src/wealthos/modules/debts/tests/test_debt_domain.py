"""Debt aggregate domain tests."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.exceptions import (
    DebtAlreadyArchived,
    DebtAlreadyPaidOff,
    InvalidMinimumPayment,
    InvalidPaymentDay,
)
from wealthos.shared.domain.value_objects.money import Money


def _make_debt(**overrides) -> Debt:
    defaults = {
        "organization_id": uuid4(),
        "account_id": uuid4(),
        "name": "Tarjeta Nu",
        "debt_type": "credit_card",
        "annual_interest_rate": Decimal("42.5"),
        "minimum_payment": Money(Decimal("500.00"), "MXN"),
    }
    defaults.update(overrides)
    return Debt.create(**defaults)


def test_create_valid_debt() -> None:
    debt = _make_debt()
    assert debt.status.is_active
    assert debt.name.value == "Tarjeta Nu"
    assert debt.debt_type.value == "credit_card"
    assert debt.paid_off_at is None
    assert debt.archived_at is None


def test_rejects_non_positive_minimum_payment() -> None:
    with pytest.raises(InvalidMinimumPayment):
        _make_debt(minimum_payment=Money(Decimal("0.00"), "MXN"))


def test_rejects_original_principal_currency_mismatch() -> None:
    with pytest.raises(InvalidMinimumPayment):
        _make_debt(original_principal=Money(Decimal("1000.00"), "USD"))


def test_rejects_negative_original_principal() -> None:
    with pytest.raises(InvalidMinimumPayment):
        Debt.create(
            organization_id=uuid4(),
            account_id=uuid4(),
            name="Tarjeta",
            debt_type="credit_card",
            annual_interest_rate=Decimal("10"),
            minimum_payment=Money(Decimal("100.00"), "MXN"),
            original_principal=Money(Decimal("-1.00"), "MXN"),
        )


def test_rejects_invalid_payment_day() -> None:
    with pytest.raises(InvalidPaymentDay):
        _make_debt(payment_day=32)
    with pytest.raises(InvalidPaymentDay):
        _make_debt(statement_day=0)


def test_rename_and_change_terms() -> None:
    debt = _make_debt()
    debt.rename("Tarjeta Nu Platino")
    assert debt.name.value == "Tarjeta Nu Platino"

    debt.change_interest_rate("39.9")
    assert debt.annual_interest_rate.annual_percentage == Decimal("39.9000")

    debt.change_minimum_payment(Money(Decimal("650.00"), "MXN"))
    assert debt.minimum_payment.amount == Decimal("650.00")

    debt.change_maturity_date(date(2030, 1, 1))
    assert debt.maturity_date == date(2030, 1, 1)

    debt.change_payment_day(15)
    assert debt.payment_day == 15

    debt.change_statement_day(1)
    assert debt.statement_day == 1

    debt.change_notes("  Renegociada  ")
    assert debt.notes == "Renegociada"
    debt.change_notes(None)
    assert debt.notes is None


def test_change_minimum_payment_rejects_currency_change() -> None:
    debt = _make_debt()
    with pytest.raises(InvalidMinimumPayment):
        debt.change_minimum_payment(Money(Decimal("100.00"), "USD"))


def test_change_minimum_payment_rejects_non_positive() -> None:
    debt = _make_debt()
    with pytest.raises(InvalidMinimumPayment):
        debt.change_minimum_payment(Money(Decimal("0.00"), "MXN"))


def test_mark_paid_off_and_archive_lifecycle() -> None:
    debt = _make_debt()
    debt.mark_paid_off()
    assert debt.status.is_paid_off
    assert debt.paid_off_at is not None

    with pytest.raises(DebtAlreadyPaidOff):
        debt.mark_paid_off()

    debt.archive()
    assert debt.status.is_archived
    assert debt.archived_at is not None

    with pytest.raises(DebtAlreadyArchived):
        debt.archive()


def test_cannot_mark_archived_debt_paid_off() -> None:
    debt = _make_debt()
    debt.archive()
    with pytest.raises(DebtAlreadyArchived):
        debt.mark_paid_off()


def test_cannot_mutate_archived_debt() -> None:
    debt = _make_debt()
    debt.archive()
    with pytest.raises(DebtAlreadyArchived):
        debt.rename("Otro nombre")


def test_ensure_accepts_payment() -> None:
    debt = _make_debt()
    debt.ensure_accepts_payment()  # no raise

    paid_off = _make_debt()
    paid_off.mark_paid_off()
    with pytest.raises(DebtAlreadyPaidOff):
        paid_off.ensure_accepts_payment()

    archived = _make_debt()
    archived.archive()
    with pytest.raises(DebtAlreadyArchived):
        archived.ensure_accepts_payment()
