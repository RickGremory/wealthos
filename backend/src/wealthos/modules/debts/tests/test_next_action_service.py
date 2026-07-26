"""NextActionService unit tests."""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.services.next_action_service import (
    CommitmentNextActionType,
    NextActionService,
)
from wealthos.shared.domain.value_objects.money import Money


def _debt(**overrides) -> Debt:
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


def test_overdue_yields_pay_overdue() -> None:
    debt = _debt()
    debt.created_at = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    action = NextActionService().for_debt(
        debt,
        account_balance=Decimal("-10000.00"),
        today=date(2026, 7, 25),
    )
    assert action.type == CommitmentNextActionType.PAY_OVERDUE
    assert action.reason_code == "overdue"
    assert action.amount == Decimal("1250.00")
    assert action.due_date == date(2026, 7, 20)


def test_missing_payment_schedule() -> None:
    action = NextActionService().for_debt(
        _debt(minimum_payment=None, scheduled_payment=None, due_day=None),
        account_balance=Decimal("-5000.00"),
        today=date(2026, 7, 10),
    )
    assert action.type == CommitmentNextActionType.CONFIGURE_PAYMENT


def test_avalanche_missing_rate() -> None:
    action = NextActionService().for_debt(
        _debt(interest_rate=None),
        account_balance=Decimal("-5000.00"),
        today=date(2026, 7, 10),
        strategy="avalanche",
    )
    assert action.type == CommitmentNextActionType.CONFIGURE_INTEREST_RATE


def test_strategy_priority() -> None:
    action = NextActionService().for_debt(
        _debt(due_day=None),
        account_balance=Decimal("-5000.00"),
        today=date(2026, 7, 10),
        is_strategy_priority=True,
        strategy="snowball",
    )
    assert action.type == CommitmentNextActionType.PAY_PRIORITY_DEBT
    assert action.reason_code == "lowest_balance"
