"""Transaction response schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from wealthos.modules.transactions.domain.entities.transaction import Transaction


class TransactionEntryResponse(BaseModel):
    id: UUID
    account_id: UUID
    amount: Decimal
    currency: str


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    transaction_type: str
    description: str
    category_id: UUID | None
    occurred_at: datetime
    notes: str | None
    status: str
    entries: list[TransactionEntryResponse]
    created_by_user_id: UUID
    updated_by_user_id: UUID
    voided_by_user_id: UUID | None
    created_at: datetime
    updated_at: datetime
    voided_at: datetime | None
    source_account_id: UUID | None = None
    destination_account_id: UUID | None = None
    amount: Decimal | None = None

    @classmethod
    def from_entity(cls, transaction: Transaction) -> TransactionResponse:
        entries = [
            TransactionEntryResponse(
                id=entry.id,
                account_id=entry.account_id,
                amount=entry.amount.amount,
                currency=entry.amount.currency.value,
            )
            for entry in transaction.entries
        ]
        source_account_id = None
        destination_account_id = None
        amount: Decimal | None = None
        if transaction.transaction_type.is_transfer and len(transaction.entries) == 2:
            debit = next(e for e in transaction.entries if e.amount.amount < 0)
            credit = next(e for e in transaction.entries if e.amount.amount > 0)
            source_account_id = debit.account_id
            destination_account_id = credit.account_id
            amount = credit.amount.amount
        elif len(transaction.entries) == 1:
            amount = abs(transaction.entries[0].amount.amount)

        return cls(
            id=transaction.id,
            organization_id=transaction.organization_id,
            transaction_type=transaction.transaction_type.value,
            description=transaction.description.value,
            category_id=transaction.category_id,
            occurred_at=transaction.occurred_at,
            notes=transaction.notes,
            status=transaction.status.value,
            entries=entries,
            created_by_user_id=transaction.created_by_user_id,
            updated_by_user_id=transaction.updated_by_user_id,
            voided_by_user_id=transaction.voided_by_user_id,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
            voided_at=transaction.voided_at,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            amount=amount,
        )
