"""DebtStrategySimulator tests: avalanche vs snowball, multi-currency separation."""

from decimal import Decimal
from uuid import uuid4

import pytest

from wealthos.modules.debts.application.services.debt_strategy_simulator import (
    DebtStrategySimulator,
    StrategyDebtState,
)
from wealthos.modules.debts.domain.exceptions import InvalidPayoffStrategy


def _debt(name: str, balance: str, rate: str, minimum: str) -> StrategyDebtState:
    return StrategyDebtState(
        debt_id=uuid4(),
        name=name,
        balance=Decimal(balance),
        annual_interest_rate=Decimal(rate),
        minimum_payment=Decimal(minimum),
    )


def test_avalanche_prioritizes_highest_interest_rate_first() -> None:
    simulator = DebtStrategySimulator()
    high_rate = _debt("Tarjeta alta tasa", "5000.00", "42.00", "100.00")
    low_rate = _debt("Prestamo baja tasa", "5000.00", "8.00", "100.00")

    result = simulator.simulate(
        strategy="avalanche",
        currency="MXN",
        debts=[low_rate, high_rate],
        extra_monthly_payment=Decimal("500.00"),
    )
    by_id = {row.debt_id: row for row in result.debts}
    assert by_id[high_rate.debt_id].priority == 1
    assert by_id[low_rate.debt_id].priority == 2


def test_snowball_prioritizes_smallest_balance_first() -> None:
    simulator = DebtStrategySimulator()
    small_balance = _debt("Deuda chica", "1000.00", "10.00", "100.00")
    large_balance = _debt("Deuda grande", "9000.00", "30.00", "100.00")

    result = simulator.simulate(
        strategy="snowball",
        currency="MXN",
        debts=[large_balance, small_balance],
        extra_monthly_payment=Decimal("500.00"),
    )
    by_id = {row.debt_id: row for row in result.debts}
    assert by_id[small_balance.debt_id].priority == 1
    assert by_id[large_balance.debt_id].priority == 2


def test_minimum_only_ignores_extra_payment() -> None:
    simulator = DebtStrategySimulator()
    debts = [_debt("Solo A", "1000.00", "12.00", "200.00")]
    with_extra = simulator.simulate(
        strategy="minimum_only",
        currency="MXN",
        debts=debts,
        extra_monthly_payment=Decimal("500.00"),
    )
    without_extra = simulator.simulate(
        strategy="minimum_only",
        currency="MXN",
        debts=debts,
        extra_monthly_payment=Decimal("0.00"),
    )
    assert with_extra.months_remaining == without_extra.months_remaining


def test_multi_currency_plans_are_computed_independently() -> None:
    simulator = DebtStrategySimulator()
    mxn_debts = [_debt("Tarjeta MXN", "10000.00", "36.00", "400.00")]
    usd_debts = [_debt("Tarjeta USD", "500.00", "18.00", "50.00")]

    mxn_plan = simulator.simulate(
        strategy="avalanche",
        currency="MXN",
        debts=mxn_debts,
        extra_monthly_payment=Decimal("0.00"),
    )
    usd_plan = simulator.simulate(
        strategy="avalanche",
        currency="USD",
        debts=usd_debts,
        extra_monthly_payment=Decimal("0.00"),
    )

    assert mxn_plan.currency == "MXN"
    assert usd_plan.currency == "USD"
    assert len(mxn_plan.debts) == 1
    assert len(usd_plan.debts) == 1
    assert mxn_plan.debts[0].debt_id == mxn_debts[0].debt_id
    assert usd_plan.debts[0].debt_id == usd_debts[0].debt_id
    # Independent state: the smaller/cheaper USD debt pays off much sooner.
    assert usd_plan.months_remaining < mxn_plan.months_remaining


def test_no_active_debts_returns_immediately_paid_off_plan() -> None:
    simulator = DebtStrategySimulator()
    result = simulator.simulate(strategy="avalanche", currency="MXN", debts=[])
    assert result.is_payment_sufficient
    assert result.months_remaining == 0
    assert result.debts == ()


def test_insolvent_minimum_only_marks_insufficient() -> None:
    simulator = DebtStrategySimulator()
    debts = [_debt("Deuda imposible", "100000.00", "90.00", "10.00")]
    result = simulator.simulate(
        strategy="minimum_only",
        currency="MXN",
        debts=debts,
        extra_monthly_payment=Decimal("0.00"),
    )
    assert result.is_payment_sufficient is False


def test_invalid_strategy_raises() -> None:
    simulator = DebtStrategySimulator()
    with pytest.raises(InvalidPayoffStrategy):
        simulator.simulate(strategy="paused", currency="MXN", debts=[])
