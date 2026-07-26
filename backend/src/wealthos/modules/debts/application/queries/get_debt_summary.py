"""GetDebtSummaryQuery — per-currency aggregates + commitment overview metrics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.debts.domain.services.debt_state_service import (
    CommitmentDisplayStatus,
    DebtStateService,
)

_ZERO = Decimal("0.00")
_RATE_PLACES = Decimal("0.000001")
_ATTENTION = frozenset(
    {
        CommitmentDisplayStatus.OVERDUE,
        CommitmentDisplayStatus.DUE_SOON,
        CommitmentDisplayStatus.DEFAULTED,
    }
)


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
class CommitmentUpcomingDue:
    commitment_id: UUID
    name: str
    currency: str
    due_date: date
    days_until_due: int
    amount: Decimal | None


@dataclass(frozen=True, slots=True)
class CommitmentAttentionItem:
    commitment_id: UUID
    code: str
    message: str
    name: str
    currency: str


@dataclass(frozen=True, slots=True)
class DebtSummary:
    by_currency: tuple[DebtSummaryByCurrency, ...]
    active_commitments: int = 0
    commitments_needing_attention: int = 0
    next_due: CommitmentUpcomingDue | None = None
    attention: tuple[CommitmentAttentionItem, ...] = ()
    next_due_by_currency: tuple[CommitmentUpcomingDue, ...] = ()

    @property
    def groups(self) -> tuple[DebtSummaryByCurrency, ...]:
        """SPEC-002 alias for by_currency."""
        return self.by_currency


class GetDebtSummaryQuery:
    def __init__(
        self,
        debts: DebtRepository,
        accounts: AccountRepository,
        state_service: DebtStateService | None = None,
    ) -> None:
        self._debts = debts
        self._accounts = accounts
        self._state = state_service or DebtStateService()

    def execute(
        self,
        organization_id: UUID,
        *,
        today: date | None = None,
    ) -> DebtSummary:
        today = today or date.today()
        debts = self._debts.list_by_organization(organization_id, include_archived=False)

        buckets: dict[str, dict] = {}
        active_count = 0
        attention_count = 0
        attention_items: list[CommitmentAttentionItem] = []
        next_due: CommitmentUpcomingDue | None = None
        next_due_by_currency: dict[str, CommitmentUpcomingDue] = {}

        for debt in debts:
            account = self._accounts.get_by_id(organization_id, debt.account_id)
            if account is None:
                continue
            raw = account.current_balance.amount
            snap = self._state.snapshot(debt, account_balance=raw, today=today)

            if debt.status.is_active:
                active_count += 1

            if snap.display_status in _ATTENTION:
                attention_count += 1
                code = snap.display_status.value
                if code == "overdue":
                    message = f"Pago vencido de {debt.name.value}."
                elif code == "due_soon":
                    days = snap.days_until_due
                    message = (
                        f"{debt.name.value} vence en {days} día(s)."
                        if days is not None
                        else f"{debt.name.value} vence pronto."
                    )
                else:
                    message = f"{debt.name.value} está en mora."
                attention_items.append(
                    CommitmentAttentionItem(
                        commitment_id=debt.id,
                        code=code,
                        message=message,
                        name=debt.name.value,
                        currency=debt.currency,
                    )
                )

            if (
                snap.next_due_date is not None
                and snap.days_until_due is not None
                and snap.owed_balance > _ZERO
                and debt.status.is_active
            ):
                required = None
                if debt.scheduled_payment is not None:
                    required = debt.scheduled_payment.amount
                elif debt.minimum_payment is not None:
                    required = debt.minimum_payment.amount
                candidate = CommitmentUpcomingDue(
                    commitment_id=debt.id,
                    name=debt.name.value,
                    currency=debt.currency,
                    due_date=snap.next_due_date,
                    days_until_due=snap.days_until_due,
                    amount=required,
                )
                if next_due is None or (
                    candidate.due_date,
                    candidate.days_until_due,
                ) < (next_due.due_date, next_due.days_until_due):
                    next_due = candidate
                current_best = next_due_by_currency.get(debt.currency)
                if current_best is None or (
                    candidate.due_date,
                    candidate.days_until_due,
                ) < (current_best.due_date, current_best.days_until_due):
                    next_due_by_currency[debt.currency] = candidate

            if not debt.status.is_active:
                continue

            currency = debt.currency
            balance = snap.owed_balance
            rate = (
                debt.interest_rate.annual_percentage
                if debt.interest_rate is not None
                else _ZERO
            )
            required = _ZERO
            if debt.scheduled_payment is not None:
                required = debt.scheduled_payment.amount
            elif debt.minimum_payment is not None:
                required = debt.minimum_payment.amount

            bucket = buckets.setdefault(
                currency,
                {
                    "total_debt": _ZERO,
                    "total_minimum_payments": _ZERO,
                    "weighted_rate_sum": _ZERO,
                    "rate_weight": _ZERO,
                    "count": 0,
                    "highest_rate": None,
                    "highest_rate_debt_id": None,
                },
            )
            bucket["total_debt"] += balance
            bucket["total_minimum_payments"] += required
            if debt.interest_rate is not None:
                bucket["weighted_rate_sum"] += balance * rate
                bucket["rate_weight"] += balance
            bucket["count"] += 1
            if debt.interest_rate is not None and (
                bucket["highest_rate"] is None or rate > bucket["highest_rate"]
            ):
                bucket["highest_rate"] = rate
                bucket["highest_rate_debt_id"] = debt.id

        by_currency = tuple(
            DebtSummaryByCurrency(
                currency=currency,
                total_debt=bucket["total_debt"],
                total_minimum_payments=bucket["total_minimum_payments"],
                weighted_average_rate=(
                    (bucket["weighted_rate_sum"] / bucket["rate_weight"]).quantize(
                        _RATE_PLACES
                    )
                    if bucket["rate_weight"] > _ZERO
                    else Decimal("0.000000")
                ),
                active_debt_count=bucket["count"],
                highest_interest_debt_id=bucket["highest_rate_debt_id"],
                highest_interest_rate=bucket["highest_rate"],
            )
            for currency, bucket in sorted(buckets.items())
        )
        return DebtSummary(
            by_currency=by_currency,
            active_commitments=active_count,
            commitments_needing_attention=attention_count,
            next_due=next_due,
            attention=tuple(attention_items),
            next_due_by_currency=tuple(next_due_by_currency.values()),
        )
