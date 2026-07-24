"""Multi-debt payoff strategy simulation (avalanche / snowball / minimum_only)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from wealthos.modules.debts.domain.exceptions import InvalidPayoffStrategy

_ZERO = Decimal("0.00")
_CENT = Decimal("0.01")
_MAX_MONTHS = 1200
ALLOWED_STRATEGIES = frozenset({"avalanche", "snowball", "minimum_only"})


@dataclass(frozen=True, slots=True)
class StrategyDebtState:
    debt_id: UUID
    name: str
    balance: Decimal
    annual_interest_rate: Decimal
    minimum_payment: Decimal


@dataclass(frozen=True, slots=True)
class StrategyDebtResult:
    debt_id: UUID
    name: str
    priority: int
    estimated_payoff_date: date | None
    is_payment_sufficient: bool


@dataclass(frozen=True, slots=True)
class StrategyPlanResult:
    strategy: str
    currency: str
    extra_monthly_payment: Decimal
    estimated_payoff_date: date | None
    months_remaining: int | None
    estimated_total_interest: Decimal | None
    debts: tuple[StrategyDebtResult, ...]
    is_payment_sufficient: bool


class DebtStrategySimulator:
    def simulate(
        self,
        *,
        strategy: str,
        currency: str,
        debts: list[StrategyDebtState],
        extra_monthly_payment: Decimal = Decimal("0"),
        start_date: date | None = None,
    ) -> StrategyPlanResult:
        cleaned = strategy.strip().lower()
        if cleaned not in ALLOWED_STRATEGIES:
            allowed = ", ".join(sorted(ALLOWED_STRATEGIES))
            raise InvalidPayoffStrategy(f"Strategy must be one of: {allowed}.")

        start = start_date or date.today()
        extra = Decimal(str(extra_monthly_payment)).quantize(_CENT, rounding=ROUND_HALF_UP)
        active = [
            {
                "debt_id": item.debt_id,
                "name": item.name,
                "balance": Decimal(str(item.balance)).quantize(_CENT, rounding=ROUND_HALF_UP),
                "rate": Decimal(str(item.annual_interest_rate)),
                "minimum": Decimal(str(item.minimum_payment)).quantize(
                    _CENT,
                    rounding=ROUND_HALF_UP,
                ),
                "payoff_date": None,
            }
            for item in debts
            if Decimal(str(item.balance)) > _ZERO
        ]

        if not active:
            return StrategyPlanResult(
                strategy=cleaned,
                currency=currency,
                extra_monthly_payment=extra,
                estimated_payoff_date=start,
                months_remaining=0,
                estimated_total_interest=_ZERO,
                debts=(),
                is_payment_sufficient=True,
            )

        ordered = self._prioritize(active, cleaned)
        priorities = {row["debt_id"]: index + 1 for index, row in enumerate(ordered)}
        total_interest = _ZERO
        months = 0

        while any(row["balance"] > _ZERO for row in ordered) and months < _MAX_MONTHS:
            months += 1
            # Accrue interest first.
            for row in ordered:
                if row["balance"] <= _ZERO:
                    continue
                monthly_rate = (row["rate"] / Decimal("1200")).quantize(
                    Decimal("0.00000001"),
                    rounding=ROUND_HALF_UP,
                )
                interest = (row["balance"] * monthly_rate).quantize(
                    _CENT,
                    rounding=ROUND_HALF_UP,
                )
                row["balance"] = (row["balance"] + interest).quantize(
                    _CENT,
                    rounding=ROUND_HALF_UP,
                )
                total_interest += interest

            # Minimum payments (skip paid-off).
            leftover_minima = _ZERO
            for row in ordered:
                if row["balance"] <= _ZERO:
                    continue
                pay = min(row["minimum"], row["balance"])
                if pay <= _ZERO:
                    continue
                # Insufficient minimum vs interest already accrued into balance —
                # if minimum cannot reduce principal meaningfully when rate is high,
                # we still apply it; insolvency detected if no progress after loop.
                row["balance"] = (row["balance"] - pay).quantize(
                    _CENT,
                    rounding=ROUND_HALF_UP,
                )
                if row["balance"] <= _ZERO:
                    row["balance"] = _ZERO
                    row["payoff_date"] = _add_months(start, months)
                    leftover_minima += row["minimum"]

            # Extra + freed minima to highest priority remaining debt.
            pool = extra + leftover_minima
            if cleaned != "minimum_only" and pool > _ZERO:
                target = next((row for row in ordered if row["balance"] > _ZERO), None)
                if target is not None:
                    pay = min(pool, target["balance"])
                    target["balance"] = (target["balance"] - pay).quantize(
                        _CENT,
                        rounding=ROUND_HALF_UP,
                    )
                    if target["balance"] <= _ZERO:
                        target["balance"] = _ZERO
                        target["payoff_date"] = _add_months(start, months)

            # Detect permanent insolvency: all remaining debts have min <= monthly interest.
            if all(
                row["balance"] <= _ZERO
                or row["minimum"]
                <= (row["balance"] * (row["rate"] / Decimal("1200"))).quantize(
                    _CENT,
                    rounding=ROUND_HALF_UP,
                )
                for row in ordered
            ) and any(row["balance"] > _ZERO for row in ordered):
                # Only fail if extra also cannot help (minimum_only or extra=0 on high rates).
                if cleaned == "minimum_only" or extra <= _ZERO:
                    return StrategyPlanResult(
                        strategy=cleaned,
                        currency=currency,
                        extra_monthly_payment=extra,
                        estimated_payoff_date=None,
                        months_remaining=None,
                        estimated_total_interest=None,
                        debts=tuple(
                            StrategyDebtResult(
                                debt_id=row["debt_id"],
                                name=row["name"],
                                priority=priorities[row["debt_id"]],
                                estimated_payoff_date=row["payoff_date"],
                                is_payment_sufficient=row["balance"] <= _ZERO,
                            )
                            for row in ordered
                        ),
                        is_payment_sufficient=False,
                    )

        if any(row["balance"] > _ZERO for row in ordered):
            return StrategyPlanResult(
                strategy=cleaned,
                currency=currency,
                extra_monthly_payment=extra,
                estimated_payoff_date=None,
                months_remaining=None,
                estimated_total_interest=None,
                debts=tuple(
                    StrategyDebtResult(
                        debt_id=row["debt_id"],
                        name=row["name"],
                        priority=priorities[row["debt_id"]],
                        estimated_payoff_date=row["payoff_date"],
                        is_payment_sufficient=False,
                    )
                    for row in ordered
                ),
                is_payment_sufficient=False,
            )

        return StrategyPlanResult(
            strategy=cleaned,
            currency=currency,
            extra_monthly_payment=extra,
            estimated_payoff_date=_add_months(start, months),
            months_remaining=months,
            estimated_total_interest=total_interest.quantize(
                _CENT,
                rounding=ROUND_HALF_UP,
            ),
            debts=tuple(
                StrategyDebtResult(
                    debt_id=row["debt_id"],
                    name=row["name"],
                    priority=priorities[row["debt_id"]],
                    estimated_payoff_date=row["payoff_date"] or _add_months(start, months),
                    is_payment_sufficient=True,
                )
                for row in ordered
            ),
            is_payment_sufficient=True,
        )

    def _prioritize(
        self,
        debts: list[dict],
        strategy: str,
    ) -> list[dict]:
        if strategy == "snowball":
            return sorted(
                debts,
                key=lambda row: (row["balance"], -row["rate"], row["name"]),
            )
        # avalanche + minimum_only priority for extra (minimum_only ignores extra)
        return sorted(
            debts,
            key=lambda row: (-row["rate"], row["balance"], row["name"]),
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
