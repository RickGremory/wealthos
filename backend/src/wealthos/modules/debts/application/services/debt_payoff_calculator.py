"""Single-debt monthly payoff simulation (no persistence)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal

_ZERO = Decimal("0.00")
_CENT = Decimal("0.01")
_MAX_MONTHS = 1200


@dataclass(frozen=True, slots=True)
class DebtPayoffInput:
    balance: Decimal
    annual_interest_rate: Decimal
    monthly_payment: Decimal
    extra_monthly_payment: Decimal = Decimal("0")


@dataclass(frozen=True, slots=True)
class DebtPayoffProjection:
    payoff_date: date | None
    months_remaining: int | None
    total_interest: Decimal | None
    total_paid: Decimal | None
    is_payment_sufficient: bool


class DebtPayoffCalculator:
    """Simulate payoff for one liability balance (positive display amount)."""

    def project(
        self,
        data: DebtPayoffInput,
        *,
        start_date: date | None = None,
    ) -> DebtPayoffProjection:
        balance = Decimal(str(data.balance)).quantize(_CENT, rounding=ROUND_HALF_UP)
        start = start_date or date.today()
        if balance <= _ZERO:
            return DebtPayoffProjection(
                payoff_date=start,
                months_remaining=0,
                total_interest=_ZERO,
                total_paid=_ZERO,
                is_payment_sufficient=True,
            )

        payment = (
            Decimal(str(data.monthly_payment)) + Decimal(str(data.extra_monthly_payment))
        ).quantize(_CENT, rounding=ROUND_HALF_UP)
        if payment <= _ZERO:
            return _insufficient()

        annual = Decimal(str(data.annual_interest_rate))
        monthly_rate = (annual / Decimal("1200")).quantize(
            Decimal("0.00000001"),
            rounding=ROUND_HALF_UP,
        )

        if annual == 0:
            months = int((balance / payment).to_integral_value(rounding=ROUND_CEILING))
            months = max(months, 1)
            return DebtPayoffProjection(
                payoff_date=_add_months(start, months),
                months_remaining=months,
                total_interest=_ZERO,
                total_paid=balance,
                is_payment_sufficient=True,
            )

        first_interest = (balance * monthly_rate).quantize(_CENT, rounding=ROUND_HALF_UP)
        if payment <= first_interest:
            return _insufficient()

        remaining = balance
        total_interest = _ZERO
        total_paid = _ZERO
        months = 0

        while remaining > _ZERO and months < _MAX_MONTHS:
            months += 1
            interest = (remaining * monthly_rate).quantize(_CENT, rounding=ROUND_HALF_UP)
            if payment <= interest:
                return _insufficient()
            if payment >= remaining + interest:
                total_paid += remaining + interest
                total_interest += interest
                remaining = _ZERO
                break
            principal = payment - interest
            remaining = (remaining - principal).quantize(_CENT, rounding=ROUND_HALF_UP)
            total_interest += interest
            total_paid += payment

        if remaining > _ZERO:
            return _insufficient()

        return DebtPayoffProjection(
            payoff_date=_add_months(start, months),
            months_remaining=months,
            total_interest=total_interest.quantize(_CENT, rounding=ROUND_HALF_UP),
            total_paid=total_paid.quantize(_CENT, rounding=ROUND_HALF_UP),
            is_payment_sufficient=True,
        )


def _insufficient() -> DebtPayoffProjection:
    return DebtPayoffProjection(
        payoff_date=None,
        months_remaining=None,
        total_interest=None,
        total_paid=None,
        is_payment_sufficient=False,
    )


def _add_months(start: date, months: int) -> date:
    year = start.year + (start.month - 1 + months) // 12
    month = (start.month - 1 + months) % 12 + 1
    day = min(start.day, _days_in_month(year, month))
    return date(year, month, day)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        nxt = date(year + 1, 1, 1)
    else:
        nxt = date(year, month + 1, 1)
    return (nxt - date(year, month, 1)).days
