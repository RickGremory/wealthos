"""DebtStateService — derived display status and due-day calendar rules."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.services.debt_state_service import (
    CommitmentDisplayStatus,
    DebtStateService,
    next_due_date_on_or_after,
    resolve_calendar_day,
)
from wealthos.shared.domain.value_objects.money import Money


def _card(**overrides) -> Debt:
    defaults = {
        "organization_id": uuid4(),
        "account_id": uuid4(),
        "name": "HSBC Platinum",
        "debt_type": "credit_card",
        "currency": "MXN",
        "creditor": "HSBC",
        "due_day": 20,
        "minimum_payment": Money("1250.00", "MXN"),
        "interest_rate": "42.5",
    }
    defaults.update(overrides)
    return Debt.create(**defaults)


def test_resolve_calendar_day_clamps_31_in_february() -> None:
    assert resolve_calendar_day(2027, 2, 31) == date(2027, 2, 28)
    assert resolve_calendar_day(2028, 2, 31) == date(2028, 2, 29)  # leap
    assert resolve_calendar_day(2026, 4, 31) == date(2026, 4, 30)


def test_next_due_date_rolls_to_next_month() -> None:
    assert next_due_date_on_or_after(
        due_day=20,
        on_or_after=date(2026, 7, 21),
    ) == date(2026, 8, 20)


def test_revolving_zero_balance_is_settled_not_paid_off() -> None:
    service = DebtStateService()
    debt = _card()
    snap = service.snapshot(
        debt,
        account_balance=Decimal("0.00"),
        today=date(2026, 7, 25),
    )
    assert snap.display_status == CommitmentDisplayStatus.SETTLED
    assert snap.behavior == "revolving"


def test_closed_zero_balance_is_paid_off() -> None:
    service = DebtStateService()
    debt = _card(debt_type="mortgage", due_day=12)
    debt.close()
    snap = service.snapshot(
        debt,
        account_balance=Decimal("0.00"),
        today=date(2026, 7, 25),
    )
    assert snap.display_status == CommitmentDisplayStatus.PAID_OFF


def test_overdue_when_cycle_due_passed_with_balance() -> None:
    service = DebtStateService()
    debt = _card(due_day=20)
    snap = service.snapshot(
        debt,
        account_balance=Decimal("-18450.00"),
        today=date(2026, 7, 25),
    )
    assert snap.display_status == CommitmentDisplayStatus.OVERDUE
    assert snap.next_due_date == date(2026, 8, 20)


def test_due_soon_within_window() -> None:
    service = DebtStateService()
    debt = _card(due_day=28)
    snap = service.snapshot(
        debt,
        account_balance=Decimal("-1000.00"),
        today=date(2026, 7, 25),
        due_soon_days=7,
    )
    assert snap.display_status == CommitmentDisplayStatus.DUE_SOON
    assert snap.days_until_due == 3


def test_paused_and_archived_override_balance() -> None:
    service = DebtStateService()
    paused = _card()
    paused.pause()
    snap = service.snapshot(
        paused,
        account_balance=Decimal("-10"),
        today=date(2026, 7, 1),
    )
    assert snap.display_status == CommitmentDisplayStatus.PAUSED

    archived = _card()
    archived.archive()
    snap = service.snapshot(
        archived,
        account_balance=Decimal("-10"),
        today=date(2026, 7, 1),
    )
    assert snap.display_status == CommitmentDisplayStatus.ARCHIVED
