"""DebtStrategyService ranking hierarchy tests."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.services.debt_strategy_service import DebtStrategyService
from wealthos.shared.domain.value_objects.money import Money


def _debt(**overrides) -> Debt:
    defaults = {
        "organization_id": uuid4(),
        "account_id": uuid4(),
        "name": "Debt",
        "debt_type": "credit_card",
        "currency": "MXN",
        "creditor": "Bank",
        "due_day": 28,
        "minimum_payment": Money("500.00", "MXN"),
        "interest_rate": "20.0",
        "priority": "medium",
    }
    defaults.update(overrides)
    return Debt.create(**defaults)


def test_avalanche_ranks_highest_rate_first() -> None:
    low = _debt(name="Low", interest_rate="18.0")
    high = _debt(name="High", interest_rate="45.0")
    balances = {
        low.account_id: Decimal("-10000.00"),
        high.account_id: Decimal("-5000.00"),
    }
    projection = DebtStrategyService().project(
        strategy="avalanche",
        debts=[low, high],
        balances_by_account=balances,
        today=date(2026, 7, 10),
        currency="MXN",
    )
    assert projection.status == "available"
    assert projection.ranking[0].debt.id == high.id
    assert projection.ranking[0].reason_code == "highest_interest_rate"
    assert projection.recommended_commitment_id == high.id


def test_snowball_ranks_lowest_balance_first() -> None:
    big = _debt(name="Big", interest_rate="40.0")
    small = _debt(name="Small", interest_rate="10.0")
    balances = {
        big.account_id: Decimal("-20000.00"),
        small.account_id: Decimal("-3000.00"),
    }
    projection = DebtStrategyService().project(
        strategy="snowball",
        debts=[big, small],
        balances_by_account=balances,
        today=date(2026, 7, 10),
        currency="MXN",
    )
    assert projection.ranking[0].debt.id == small.id
    assert projection.ranking[0].reason_code == "lowest_balance"


def test_overdue_outranks_strategy() -> None:
    overdue = _debt(name="Overdue", due_day=5, interest_rate="10.0")
    high = _debt(name="High", due_day=28, interest_rate="50.0")
    balances = {
        overdue.account_id: Decimal("-4000.00"),
        high.account_id: Decimal("-8000.00"),
    }
    projection = DebtStrategyService().project(
        strategy="avalanche",
        debts=[overdue, high],
        balances_by_account=balances,
        today=date(2026, 7, 25),
        currency="MXN",
    )
    assert projection.ranking[0].debt.id == overdue.id
    assert projection.ranking[0].reason_code == "overdue"


def test_avalanche_insufficient_data_without_rates() -> None:
    a = _debt(interest_rate=None)
    b = _debt(interest_rate=None)
    balances = {
        a.account_id: Decimal("-1000.00"),
        b.account_id: Decimal("-2000.00"),
    }
    projection = DebtStrategyService().project(
        strategy="avalanche",
        debts=[a, b],
        balances_by_account=balances,
        today=date(2026, 7, 10),
        currency="MXN",
    )
    assert projection.status == "insufficient_data"
    assert projection.recommended_commitment_id is None
