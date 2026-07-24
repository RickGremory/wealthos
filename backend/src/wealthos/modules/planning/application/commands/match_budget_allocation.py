"""MatchBudgetAllocation command."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.planning.application.services.cash_plan_matching_service import (
    CashPlanMatchingService,
)
from wealthos.modules.planning.domain.entities.budget_allocation_match import (
    BudgetAllocationMatch,
)
from wealthos.modules.planning.domain.exceptions import (
    BudgetAllocationNotFoundError,
    BudgetNotFoundError,
    ConcurrentMatchConflict,
    MatchAmountExceedsRemaining,
    MatchTransactionInvalid,
)
from wealthos.modules.planning.domain.repositories.budget_allocation_match_repository import (
    BudgetAllocationMatchRepository,
)
from wealthos.modules.planning.domain.repositories.budget_allocation_repository import (
    BudgetAllocationRepository,
)
from wealthos.modules.planning.domain.repositories.budget_repository import BudgetRepository
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionRepository,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class MatchBudgetAllocationInput:
    organization_id: UUID
    budget_id: UUID
    allocation_id: UUID
    transaction_id: UUID
    matched_amount: Decimal


class MatchBudgetAllocationCommand:
    def __init__(
        self,
        budgets: BudgetRepository,
        allocations: BudgetAllocationRepository,
        matches: BudgetAllocationMatchRepository,
        transactions: TransactionRepository,
        matching: CashPlanMatchingService | None = None,
    ) -> None:
        self._budgets = budgets
        self._allocations = allocations
        self._matches = matches
        self._transactions = transactions
        self._matching = matching or CashPlanMatchingService()

    def execute(self, data: MatchBudgetAllocationInput) -> BudgetAllocationMatch:
        budget = self._budgets.get_by_id(data.organization_id, data.budget_id)
        if budget is None:
            raise BudgetNotFoundError("Budget not found.")
        if budget.status.is_archived:
            raise ConcurrentMatchConflict("Cannot match against an archived budget.")

        allocation = self._allocations.get_by_id(data.organization_id, data.allocation_id)
        if allocation is None or allocation.budget_id != data.budget_id:
            raise BudgetAllocationNotFoundError("Budget allocation not found.")

        tx = self._transactions.get_by_id(data.organization_id, data.transaction_id)
        if tx is None or tx.status.is_voided:
            raise MatchTransactionInvalid("Transaction not found or voided.")

        existing = self._matches.list_by_allocation(data.organization_id, data.allocation_id)
        matched_total = sum((m.matched_amount.amount for m in existing), Decimal("0.00"))
        try:
            amount = self._matching.validate_match_amount(
                planned_amount=allocation.amount.amount,
                matched_amount=matched_total,
                match_amount=data.matched_amount,
            )
        except ValueError as exc:
            msg = str(exc)
            if "exceeds" in msg:
                raise MatchAmountExceedsRemaining(msg) from exc
            raise MatchTransactionInvalid(msg) from exc

        # Re-check remaining after validation window (optimistic concurrency).
        refreshed = self._matches.list_by_allocation(data.organization_id, data.allocation_id)
        refreshed_total = sum((m.matched_amount.amount for m in refreshed), Decimal("0.00"))
        if refreshed_total != matched_total:
            raise ConcurrentMatchConflict(
                "Allocation matches changed concurrently; retry the match."
            )

        match = BudgetAllocationMatch.create(
            organization_id=data.organization_id,
            budget_allocation_id=data.allocation_id,
            transaction_id=data.transaction_id,
            matched_amount=Money(amount, allocation.amount.currency),
        )
        return self._matches.add(match)
