"""Rank commitments for payment strategy recommendations (orient only)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.exceptions import InvalidPayoffStrategy
from wealthos.modules.debts.domain.services.debt_state_service import (
    CommitmentDisplayStatus,
    DebtStateService,
    DebtStateSnapshot,
)

ALLOWED_STRATEGIES = frozenset({"avalanche", "snowball", "minimum_only", "manual"})
_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
_ZERO = Decimal("0.00")


@dataclass(frozen=True, slots=True)
class RankedCommitment:
    position: int
    debt: Debt
    snap: DebtStateSnapshot
    reason_code: str
    eligible: bool


@dataclass(frozen=True, slots=True)
class StrategyProjection:
    status: str  # available | partial | insufficient_data | not_configured | unavailable
    strategy: str
    ranking: tuple[RankedCommitment, ...]
    recommended_commitment_id: UUID | None
    next_reason_code: str | None
    excluded_commitments: int
    warnings: tuple[str, ...]
    generated_at: date


@dataclass(frozen=True, slots=True)
class _Candidate:
    debt: Debt
    snap: DebtStateSnapshot
    overdue: bool
    due_soon: bool
    defaulted: bool
    rate: Decimal | None
    balance: Decimal
    due_key: int
    priority_key: int
    missing_rate: bool
    has_payment: bool


class DebtStrategyService:
    """Filter, hierarchical rank, and explain — never mutates ledger data."""

    def __init__(self, state_service: DebtStateService | None = None) -> None:
        self._state = state_service or DebtStateService()

    def project(
        self,
        *,
        strategy: str,
        debts: list[Debt],
        balances_by_account: dict[UUID, Decimal],
        today: date | None = None,
        currency: str | None = None,
    ) -> StrategyProjection:
        cleaned = strategy.strip().lower()
        if cleaned not in ALLOWED_STRATEGIES:
            allowed = ", ".join(sorted(ALLOWED_STRATEGIES))
            raise InvalidPayoffStrategy(f"Strategy must be one of: {allowed}.")

        today = today or date.today()
        candidates: list[_Candidate] = []
        for debt in debts:
            if currency is not None and debt.currency != currency:
                continue
            if debt.status.is_archived:
                continue
            raw = balances_by_account.get(debt.account_id, _ZERO)
            snap = self._state.snapshot(debt, account_balance=raw, today=today)
            owed = snap.owed_balance
            rate = (
                debt.interest_rate.annual_percentage if debt.interest_rate is not None else None
            )
            has_payment = (
                debt.minimum_payment is not None or debt.scheduled_payment is not None
            )
            due_key = (
                snap.days_until_due
                if snap.days_until_due is not None
                else 10_000
            )
            candidates.append(
                _Candidate(
                    debt=debt,
                    snap=snap,
                    overdue=snap.display_status == CommitmentDisplayStatus.OVERDUE,
                    due_soon=snap.display_status == CommitmentDisplayStatus.DUE_SOON,
                    defaulted=debt.status.is_defaulted,
                    rate=rate,
                    balance=owed,
                    due_key=due_key,
                    priority_key=_PRIORITY_RANK.get(debt.priority.value, 1),
                    missing_rate=rate is None,
                    has_payment=has_payment,
                )
            )

        eligible = [
            c
            for c in candidates
            if c.debt.status.is_active and c.balance > _ZERO and not c.defaulted
        ]
        excluded = len(candidates) - len(eligible)

        if not eligible and not any(c.defaulted for c in candidates):
            return StrategyProjection(
                status="not_configured",
                strategy=cleaned,
                ranking=(),
                recommended_commitment_id=None,
                next_reason_code=None,
                excluded_commitments=excluded,
                warnings=(),
                generated_at=today,
            )

        warnings: list[str] = []
        ranking_pool = list(eligible)

        if cleaned == "avalanche":
            with_rate = [c for c in ranking_pool if not c.missing_rate]
            missing = len(ranking_pool) - len(with_rate)
            if missing and with_rate:
                warnings.append(
                    f"Recommendation uses only commitments with a registered interest rate "
                    f"({missing} excluded)."
                )
                ranking_pool = with_rate
                status = "partial"
            elif missing and not with_rate:
                return StrategyProjection(
                    status="insufficient_data",
                    strategy=cleaned,
                    ranking=(),
                    recommended_commitment_id=None,
                    next_reason_code="missing_interest_rate",
                    excluded_commitments=excluded + missing,
                    warnings=(
                        "Cannot apply Avalanche: no eligible commitments have an interest rate.",
                    ),
                    generated_at=today,
                )
            else:
                status = "available"
        else:
            status = "available"

        # Defaulted show as attention, not normal strategy participants.
        attention = [c for c in candidates if c.defaulted and c.balance > _ZERO]

        ordered = self._sort(ranking_pool, cleaned)
        ranked: list[RankedCommitment] = []
        position = 1
        for item in attention:
            ranked.append(
                RankedCommitment(
                    position=position,
                    debt=item.debt,
                    snap=item.snap,
                    reason_code="defaulted_commitment",
                    eligible=False,
                )
            )
            position += 1

        for item in ordered:
            ranked.append(
                RankedCommitment(
                    position=position,
                    debt=item.debt,
                    snap=item.snap,
                    reason_code=self._reason_for(item, cleaned),
                    eligible=True,
                )
            )
            position += 1

        recommended = next((r for r in ranked if r.eligible), None)
        return StrategyProjection(
            status=status,
            strategy=cleaned,
            ranking=tuple(ranked),
            recommended_commitment_id=(
                recommended.debt.id if recommended is not None else None
            ),
            next_reason_code=recommended.reason_code if recommended else None,
            excluded_commitments=excluded,
            warnings=tuple(warnings),
            generated_at=today,
        )

    def _sort(self, pool: list[_Candidate], strategy: str) -> list[_Candidate]:
        def tier(c: _Candidate) -> tuple:
            # Hierarchy: overdue → due soon → strategy → manual priority
            urgency = 0 if c.overdue else (1 if c.due_soon else 2)
            if strategy == "avalanche":
                rate_key = -(c.rate or _ZERO)
                return (urgency, rate_key, c.due_key, c.balance, c.priority_key)
            if strategy == "snowball":
                return (urgency, c.balance, -(c.rate or _ZERO), c.due_key, c.priority_key)
            if strategy == "minimum_only":
                return (urgency, c.due_key, c.priority_key, c.balance)
            # manual
            return (urgency, c.priority_key, c.due_key, c.balance)

        return sorted(pool, key=tier)

    def _reason_for(self, item: _Candidate, strategy: str) -> str:
        if item.overdue:
            return "overdue"
        if item.due_soon:
            return "due_soon"
        if strategy == "avalanche":
            return "highest_interest_rate"
        if strategy == "snowball":
            return "lowest_balance"
        if strategy == "minimum_only":
            return "minimum_payment_required"
        return "manual_priority"
