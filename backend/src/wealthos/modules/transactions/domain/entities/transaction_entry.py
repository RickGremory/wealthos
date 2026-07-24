"""Transaction entry — signed monetary movement against one account."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.transactions.domain.exceptions import ZeroEntryAmount
from wealthos.shared.domain.value_objects.money import Money


@dataclass(slots=True)
class TransactionEntry:
    id: UUID
    transaction_id: UUID
    account_id: UUID
    amount: Money
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        transaction_id: UUID,
        account_id: UUID,
        amount: Money,
        entry_id: UUID | None = None,
    ) -> TransactionEntry:
        if amount.amount == Decimal("0.00"):
            raise ZeroEntryAmount("Transaction entry amount cannot be zero.")
        return cls(
            id=entry_id or uuid4(),
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
            created_at=datetime.now(UTC),
        )
