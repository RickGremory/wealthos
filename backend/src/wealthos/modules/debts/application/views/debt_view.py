"""Debt + derived balance/payoff projection (not persisted)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.debts.application.services.debt_payoff_calculator import (
    DebtPayoffCalculator,
    DebtPayoffInput,
    DebtPayoffProjection,
)
from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.shared.domain.value_objects.money import Money

_ZERO = Decimal("0.00")


@dataclass(frozen=True, slots=True)
class DebtWithBalance:
    debt: Debt
    current_balance: Money
    payoff: DebtPayoffProjection | None


def build_debt_with_balance(
    debt: Debt,
    account: Account | None,
    calculator: DebtPayoffCalculator,
) -> DebtWithBalance:
    """Attach a positive display balance and payoff projection to a debt.

    Balances always come from the linked liability Account (never stored on
    Debt itself); the account balance is negative internally and displayed
    as a positive amount here.
    """
    currency = debt.minimum_payment.currency
    if account is None:
        return DebtWithBalance(
            debt=debt,
            current_balance=Money(_ZERO, currency),
            payoff=None,
        )

    current_balance = Money(abs(account.current_balance.amount), currency)
    payoff: DebtPayoffProjection | None = None
    if debt.status.is_active:
        payoff = calculator.project(
            DebtPayoffInput(
                balance=current_balance.amount,
                annual_interest_rate=debt.annual_interest_rate.annual_percentage,
                monthly_payment=debt.minimum_payment.amount,
            )
        )
    return DebtWithBalance(debt=debt, current_balance=current_balance, payoff=payoff)
