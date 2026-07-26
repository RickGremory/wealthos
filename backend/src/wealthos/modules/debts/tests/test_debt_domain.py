"""Debt aggregate domain tests (SPEC-002 Phase 1)."""

from decimal import Decimal
from uuid import uuid4

import pytest

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.exceptions import (
    DebtAlreadyArchived,
    DebtAlreadyClosed,
    DebtAlreadyPaused,
    DebtNotPaused,
    InvalidCalendarDay,
    InvalidPaymentAmount,
)
from wealthos.shared.domain.value_objects.money import Money


def _make_debt(**overrides) -> Debt:
    defaults = {
        "organization_id": uuid4(),
        "account_id": uuid4(),
        "name": "Tarjeta Nu",
        "debt_type": "credit_card",
        "currency": "MXN",
        "creditor": "Nu",
        "priority": "high",
        "interest_rate": Decimal("42.5"),
        "minimum_payment": Money(Decimal("500.00"), "MXN"),
    }
    defaults.update(overrides)
    return Debt.create(**defaults)


def test_create_valid_debt_with_optional_enrichment() -> None:
    debt = _make_debt()
    assert debt.status.is_active
    assert debt.priority.value == "high"
    assert debt.creditor == "Nu"
    assert debt.currency == "MXN"
    assert debt.interest_rate is not None
    assert debt.interest_rate.annual_percentage == Decimal("42.500000")
    assert debt.version == 1
    assert debt.closed_at is None
    assert debt.debt_type.behavior == "revolving"


def test_create_minimal_debt_without_rate_or_payments() -> None:
    debt = Debt.create(
        organization_id=uuid4(),
        account_id=uuid4(),
        name="Préstamo familiar",
        debt_type="family_loan",
        currency="MXN",
        creditor="Papá",
    )
    assert debt.interest_rate is None
    assert debt.minimum_payment is None
    assert debt.scheduled_payment is None
    assert debt.debt_type.behavior == "installment"


def test_rejects_zero_minimum_when_set() -> None:
    with pytest.raises(InvalidPaymentAmount):
        _make_debt(minimum_payment=Money(Decimal("0.00"), "MXN"))


def test_rejects_currency_mismatch_on_optional_money() -> None:
    with pytest.raises(InvalidPaymentAmount):
        _make_debt(original_amount=Money(Decimal("1000.00"), "USD"))


def test_rejects_invalid_due_day() -> None:
    with pytest.raises(InvalidCalendarDay):
        _make_debt(due_day=32)
    with pytest.raises(InvalidCalendarDay):
        _make_debt(statement_day=0)


def test_rename_and_change_terms_then_bump_version() -> None:
    debt = _make_debt()
    assert debt.version == 1
    debt.rename("Tarjeta Nu Platino")
    assert debt.name.value == "Tarjeta Nu Platino"
    assert debt.version == 1

    debt.change_interest_rate("39.9")
    assert debt.interest_rate is not None
    assert debt.interest_rate.annual_percentage == Decimal("39.900000")

    debt.change_minimum_payment(Money(Decimal("650.00"), "MXN"))
    debt.change_due_day(15)
    assert debt.due_day == 15
    debt.change_interest_rate(None)
    assert debt.interest_rate is None

    debt.bump_version()
    assert debt.version == 2


def test_pause_resume_close_archive_lifecycle() -> None:
    debt = _make_debt()
    debt.pause()
    assert debt.status.is_paused
    with pytest.raises(DebtAlreadyPaused):
        debt.pause()

    debt.resume()
    assert debt.status.is_active
    with pytest.raises(DebtNotPaused):
        debt.resume()

    debt.close()
    assert debt.status.is_closed
    assert debt.closed_at is not None
    with pytest.raises(DebtAlreadyClosed):
        debt.close()

    debt.archive()
    assert debt.status.is_archived
    with pytest.raises(DebtAlreadyArchived):
        debt.archive()


def test_cannot_mutate_closed_or_archived() -> None:
    closed = _make_debt()
    closed.close()
    with pytest.raises(DebtAlreadyClosed):
        closed.rename("x")

    archived = _make_debt()
    archived.archive()
    with pytest.raises(DebtAlreadyArchived):
        archived.rename("x")


def test_ensure_accepts_payment() -> None:
    debt = _make_debt()
    debt.ensure_accepts_payment()

    paused = _make_debt()
    paused.pause()
    with pytest.raises(DebtAlreadyPaused):
        paused.ensure_accepts_payment()

    closed = _make_debt()
    closed.close()
    with pytest.raises(DebtAlreadyClosed):
        closed.ensure_accepts_payment()
