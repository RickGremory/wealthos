"""Debt + derived balance/payoff projection (not persisted)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.debts.application.services.debt_payoff_calculator import (
    DebtPayoffCalculator,
    DebtPayoffInput,
    DebtPayoffProjection,
)
from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.services.debt_state_service import DebtStateService
from wealthos.modules.debts.domain.services.next_action_service import (
    CommitmentNextAction,
    NextActionService,
)
from wealthos.shared.domain.value_objects.money import Money

_ZERO = Decimal("0.00")
_PCT = Decimal("0.01")


def utilization_percentage(
    *,
    owed_balance: Decimal,
    credit_limit: Decimal | None,
) -> Decimal | None:
    """balance / credit_limit × 100 when limit > 0; None if no limit."""
    if credit_limit is None or credit_limit <= _ZERO:
        return None
    if owed_balance <= _ZERO:
        return Decimal("0.00")
    return (owed_balance / credit_limit * Decimal("100")).quantize(_PCT)


@dataclass(frozen=True, slots=True)
class DebtWithBalance:
    debt: Debt
    current_balance: Money
    payoff: DebtPayoffProjection | None
    display_status: str | None = None
    next_due_date: date | None = None
    days_until_due: int | None = None
    utilization_percentage: Decimal | None = None
    next_action: CommitmentNextAction | None = None


def build_debt_with_balance(
    debt: Debt,
    account: Account | None,
    calculator: DebtPayoffCalculator,
    *,
    state_service: DebtStateService | None = None,
    next_action_service: NextActionService | None = None,
    strategy: str | None = None,
    is_strategy_priority: bool = False,
    today: date | None = None,
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

    state = state_service or DebtStateService()
    snap = state.snapshot(debt, account_balance=raw_balance, today=today)
    display_status = snap.display_status.value

    util = utilization_percentage(
        owed_balance=snap.owed_balance,
        credit_limit=debt.credit_limit.amount if debt.credit_limit else None,
    )

    next_svc = next_action_service or NextActionService(state)
    action = next_svc.from_snapshot(
        debt,
        snap,
        is_strategy_priority=is_strategy_priority,
        strategy=strategy,
    )

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
        next_due_date=snap.next_due_date,
        days_until_due=snap.days_until_due,
        utilization_percentage=util,
        next_action=action,
    )
