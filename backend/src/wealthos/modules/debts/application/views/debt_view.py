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
from wealthos.modules.debts.domain.services.debt_state_service import DebtStateService
from wealthos.shared.domain.value_objects.money import Money

_ZERO = Decimal("0.00")


@dataclass(frozen=True, slots=True)
class DebtWithBalance:
    debt: Debt
    current_balance: Money
    payoff: DebtPayoffProjection | None
    display_status: str | None = None


def build_debt_with_balance(
    debt: Debt,
    account: Account | None,
    calculator: DebtPayoffCalculator,
    *,
    state_service: DebtStateService | None = None,
) -> DebtWithBalance:
    """Attach a positive display balance and payoff projection to a debt.

    Balances always come from the linked liability Account (never stored on
    Debt itself); the account balance is negative internally and displayed
    as a positive amount here.
    """
    currency = debt.currency
    if account is None:
        return DebtWithBalance(
            debt=debt,
            current_balance=Money(_ZERO, currency),
            payoff=None,
            display_status=None,
        )

    raw_balance = account.current_balance.amount
    current_balance = Money(abs(raw_balance) if raw_balance < 0 else _ZERO, currency)

    display_status: str | None = None
    if state_service is not None:
        snap = state_service.snapshot(debt, account_balance=raw_balance)
        display_status = snap.display_status.value

    payoff: DebtPayoffProjection | None = None
    monthly = None
    if debt.scheduled_payment is not None:
        monthly = debt.scheduled_payment.amount
    elif debt.minimum_payment is not None:
        monthly = debt.minimum_payment.amount

    rate = (
        debt.interest_rate.annual_percentage
        if debt.interest_rate is not None
        else Decimal("0")
    )

    if debt.status.is_active and monthly is not None and current_balance.amount > 0:
        payoff = calculator.project(
            DebtPayoffInput(
                balance=current_balance.amount,
                annual_interest_rate=rate,
                monthly_payment=monthly,
            )
        )
    return DebtWithBalance(
        debt=debt,
        current_balance=current_balance,
        payoff=payoff,
        display_status=display_status,
    )
