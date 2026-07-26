"""Derive CommitmentNextAction codes for a debt + balance snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.services.debt_state_service import (
    CommitmentDisplayStatus,
    DebtStateService,
    DebtStateSnapshot,
)


class CommitmentNextActionType(StrEnum):
    PAY_OVERDUE = "pay_overdue"
    PAY_MINIMUM = "pay_minimum"
    PAY_PRIORITY_DEBT = "pay_priority_debt"
    CONFIGURE_PAYMENT = "configure_payment"
    CONFIGURE_INTEREST_RATE = "configure_interest_rate"
    REVIEW_PAUSED = "review_paused"
    NO_ACTION_REQUIRED = "no_action_required"


@dataclass(frozen=True, slots=True)
class CommitmentNextAction:
    type: CommitmentNextActionType
    reason_code: str
    amount: Decimal | None = None
    due_date: date | None = None


class NextActionService:
    def __init__(self, state_service: DebtStateService | None = None) -> None:
        self._state = state_service or DebtStateService()

    def for_debt(
        self,
        debt: Debt,
        *,
        account_balance: Decimal,
        today: date | None = None,
        is_strategy_priority: bool = False,
        strategy: str | None = None,
    ) -> CommitmentNextAction:
        today = today or date.today()
        snap = self._state.snapshot(debt, account_balance=account_balance, today=today)
        return self.from_snapshot(
            debt,
            snap,
            is_strategy_priority=is_strategy_priority,
            strategy=strategy,
        )

    def from_snapshot(
        self,
        debt: Debt,
        snap: DebtStateSnapshot,
        *,
        is_strategy_priority: bool = False,
        strategy: str | None = None,
    ) -> CommitmentNextAction:
        if snap.display_status == CommitmentDisplayStatus.PAUSED:
            return CommitmentNextAction(
                type=CommitmentNextActionType.REVIEW_PAUSED,
                reason_code="review_paused",
            )

        if snap.display_status in {
            CommitmentDisplayStatus.SETTLED,
            CommitmentDisplayStatus.PAID_OFF,
            CommitmentDisplayStatus.ARCHIVED,
        }:
            return CommitmentNextAction(
                type=CommitmentNextActionType.NO_ACTION_REQUIRED,
                reason_code="no_action_required",
            )

        if snap.display_status == CommitmentDisplayStatus.OVERDUE:
            amount = self._required_payment(debt)
            return CommitmentNextAction(
                type=CommitmentNextActionType.PAY_OVERDUE,
                reason_code="overdue",
                amount=amount,
                due_date=snap.next_due_date,
            )

        if snap.owed_balance > 0 and self._required_payment(debt) is None:
            return CommitmentNextAction(
                type=CommitmentNextActionType.CONFIGURE_PAYMENT,
                reason_code="missing_payment_schedule",
            )

        if (
            strategy == "avalanche"
            and debt.interest_rate is None
            and snap.owed_balance > 0
            and debt.status.is_active
        ):
            return CommitmentNextAction(
                type=CommitmentNextActionType.CONFIGURE_INTEREST_RATE,
                reason_code="missing_interest_rate",
            )

        if is_strategy_priority and snap.owed_balance > 0:
            return CommitmentNextAction(
                type=CommitmentNextActionType.PAY_PRIORITY_DEBT,
                reason_code=(
                    "highest_interest_rate"
                    if strategy == "avalanche"
                    else "lowest_balance"
                    if strategy == "snowball"
                    else "manual_priority"
                ),
                amount=self._required_payment(debt),
                due_date=snap.next_due_date,
            )

        if snap.display_status == CommitmentDisplayStatus.DUE_SOON:
            return CommitmentNextAction(
                type=CommitmentNextActionType.PAY_MINIMUM,
                reason_code="due_soon",
                amount=self._required_payment(debt),
                due_date=snap.next_due_date,
            )

        if snap.owed_balance > 0 and self._required_payment(debt) is not None:
            return CommitmentNextAction(
                type=CommitmentNextActionType.PAY_MINIMUM,
                reason_code="minimum_payment_required",
                amount=self._required_payment(debt),
                due_date=snap.next_due_date,
            )

        return CommitmentNextAction(
            type=CommitmentNextActionType.NO_ACTION_REQUIRED,
            reason_code="no_action_required",
        )

    @staticmethod
    def _required_payment(debt: Debt) -> Decimal | None:
        if debt.scheduled_payment is not None:
            return debt.scheduled_payment.amount
        if debt.minimum_payment is not None:
            return debt.minimum_payment.amount
        return None
