"""CashPlanItemMatch — links a transaction to a cash plan item."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.planning.domain.exceptions import InvalidCashPlanItemAmount
from wealthos.shared.domain.value_objects.money import Money


@dataclass(slots=True)
class CashPlanItemMatch:
    id: UUID
    organization_id: UUID
    cash_plan_item_id: UUID
    transaction_id: UUID
    matched_amount: Money
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        cash_plan_item_id: UUID,
        transaction_id: UUID,
        matched_amount: Money,
        match_id: UUID | None = None,
    ) -> CashPlanItemMatch:
        if matched_amount.amount <= Decimal("0.00"):
            raise InvalidCashPlanItemAmount("Matched amount must be positive.")
        return cls(
            id=match_id or uuid4(),
            organization_id=organization_id,
            cash_plan_item_id=cash_plan_item_id,
            transaction_id=transaction_id,
            matched_amount=matched_amount,
            created_at=datetime.now(UTC),
        )
