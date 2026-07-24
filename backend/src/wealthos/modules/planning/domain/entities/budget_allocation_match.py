"""BudgetAllocationMatch — links a transaction to a budget allocation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.planning.domain.exceptions import InvalidAllocationAmount
from wealthos.shared.domain.value_objects.money import Money


@dataclass(slots=True)
class BudgetAllocationMatch:
    id: UUID
    organization_id: UUID
    budget_allocation_id: UUID
    transaction_id: UUID
    matched_amount: Money
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        budget_allocation_id: UUID,
        transaction_id: UUID,
        matched_amount: Money,
        match_id: UUID | None = None,
    ) -> BudgetAllocationMatch:
        if matched_amount.amount <= Decimal("0.00"):
            raise InvalidAllocationAmount("Matched amount must be positive.")
        return cls(
            id=match_id or uuid4(),
            organization_id=organization_id,
            budget_allocation_id=budget_allocation_id,
            transaction_id=transaction_id,
            matched_amount=matched_amount,
            created_at=datetime.now(UTC),
        )
