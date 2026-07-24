"""GetDebtSummaryQuery — per-currency aggregates across active debts."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository

_ZERO = Decimal("0.00")
_RATE_PLACES = Decimal("0.0001")


@dataclass(frozen=True, slots=True)
class DebtSummaryByCurrency:
    currency: str
    total_debt: Decimal
    total_minimum_payments: Decimal
    weighted_average_rate: Decimal
    active_debt_count: int
    highest_interest_debt_id: UUID | None
    highest_interest_rate: Decimal | None


@dataclass(frozen=True, slots=True)
class DebtSummary:
    by_currency: tuple[DebtSummaryByCurrency, ...]


class GetDebtSummaryQuery:
    def __init__(self, debts: DebtRepository, accounts: AccountRepository) -> None:
        self._debts = debts
        self._accounts = accounts

    def execute(self, organization_id: UUID) -> DebtSummary:
        active_debts = self._debts.list_by_organization(organization_id, status="active")

        buckets: dict[str, dict] = {}
        for debt in active_debts:
            account = self._accounts.get_by_id(organization_id, debt.account_id)
            if account is None:
                continue
            currency = debt.minimum_payment.currency.value
            balance = abs(account.current_balance.amount)
            rate = debt.annual_interest_rate.annual_percentage

            bucket = buckets.setdefault(
                currency,
                {
                    "total_debt": _ZERO,
                    "total_minimum_payments": _ZERO,
                    "weighted_rate_sum": _ZERO,
                    "count": 0,
                    "highest_rate": None,
                    "highest_rate_debt_id": None,
                },
            )
            bucket["total_debt"] += balance
            bucket["total_minimum_payments"] += debt.minimum_payment.amount
            bucket["weighted_rate_sum"] += balance * rate
            bucket["count"] += 1
            if bucket["highest_rate"] is None or rate > bucket["highest_rate"]:
                bucket["highest_rate"] = rate
                bucket["highest_rate_debt_id"] = debt.id

        by_currency = tuple(
            DebtSummaryByCurrency(
                currency=currency,
                total_debt=bucket["total_debt"],
                total_minimum_payments=bucket["total_minimum_payments"],
                weighted_average_rate=(
                    (bucket["weighted_rate_sum"] / bucket["total_debt"]).quantize(_RATE_PLACES)
                    if bucket["total_debt"] > _ZERO
                    else Decimal("0.0000")
                ),
                active_debt_count=bucket["count"],
                highest_interest_debt_id=bucket["highest_rate_debt_id"],
                highest_interest_rate=bucket["highest_rate"],
            )
            for currency, bucket in sorted(buckets.items())
        )
        return DebtSummary(by_currency=by_currency)
