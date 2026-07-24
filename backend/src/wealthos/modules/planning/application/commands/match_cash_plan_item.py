"""MatchCashPlanItem command."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.planning.application.services.cash_plan_matching_service import (
    CashPlanMatchingService,
)
from wealthos.modules.planning.domain.entities.cash_plan_item_match import CashPlanItemMatch
from wealthos.modules.planning.domain.exceptions import (
    CashPlanItemNotFoundError,
    CashPlanNotFoundError,
    ConcurrentMatchConflict,
    MatchAmountExceedsRemaining,
    MatchTransactionInvalid,
)
from wealthos.modules.planning.domain.repositories.cash_plan_item_match_repository import (
    CashPlanItemMatchRepository,
)
from wealthos.modules.planning.domain.repositories.cash_plan_item_repository import (
    CashPlanItemRepository,
)
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionRepository,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class MatchCashPlanItemInput:
    organization_id: UUID
    cash_plan_id: UUID
    item_id: UUID
    transaction_id: UUID
    matched_amount: Decimal


class MatchCashPlanItemCommand:
    def __init__(
        self,
        cash_plans: CashPlanRepository,
        items: CashPlanItemRepository,
        matches: CashPlanItemMatchRepository,
        transactions: TransactionRepository,
        matching: CashPlanMatchingService | None = None,
    ) -> None:
        self._cash_plans = cash_plans
        self._items = items
        self._matches = matches
        self._transactions = transactions
        self._matching = matching or CashPlanMatchingService()

    def execute(self, data: MatchCashPlanItemInput) -> CashPlanItemMatch:
        plan = self._cash_plans.get_by_id(data.organization_id, data.cash_plan_id)
        if plan is None:
            raise CashPlanNotFoundError("Cash plan not found.")

        item = self._items.lock_for_update(data.organization_id, data.item_id)
        if item is None or item.cash_plan_id != data.cash_plan_id:
            raise CashPlanItemNotFoundError("Cash plan item not found.")
        try:
            item.ensure_matchable()
        except Exception as exc:
            raise ConcurrentMatchConflict(str(exc)) from exc

        tx = self._transactions.get_by_id(data.organization_id, data.transaction_id)
        if tx is None or tx.status.is_voided:
            raise MatchTransactionInvalid("Transaction not found or voided.")

        matched_total = self._matches.sum_matched_amount(data.organization_id, data.item_id)
        try:
            amount = self._matching.validate_match_amount(
                planned_amount=item.amount.amount,
                matched_amount=matched_total,
                match_amount=data.matched_amount,
            )
        except ValueError as exc:
            msg = str(exc)
            if "exceeds" in msg:
                raise MatchAmountExceedsRemaining(msg) from exc
            raise MatchTransactionInvalid(msg) from exc

        match = CashPlanItemMatch.create(
            organization_id=data.organization_id,
            cash_plan_item_id=data.item_id,
            transaction_id=data.transaction_id,
            matched_amount=Money(amount, item.amount.currency),
        )
        saved = self._matches.add(match)

        after = matched_total + amount
        new_status = self._matching.new_status(
            planned_amount=item.amount.amount,
            matched_amount_after=after,
        )
        if new_status == "matched":
            item.mark_matched()
        elif new_status == "partially_matched":
            item.mark_partially_matched()
        self._items.save(item)
        return saved
