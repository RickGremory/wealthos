"""Schemas for FX transfers."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from wealthos.modules.transactions.domain.entities.fx_transfer import FxTransfer


class FxTransferCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_account_id: UUID
    destination_account_id: UUID
    source_amount: Decimal = Field(gt=0)
    destination_amount: Decimal = Field(gt=0)
    occurred_at: datetime
    description: str = Field(min_length=1, max_length=200)
    fee_amount: Decimal | None = Field(default=None, gt=0)
    notes: str | None = Field(default=None, max_length=2000)


class FxTransferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    source_account_id: UUID
    destination_account_id: UUID
    source_amount: str
    source_currency: str
    destination_amount: str
    destination_currency: str
    effective_exchange_rate: str
    fee_amount: str | None
    fee_currency: str | None
    occurred_at: datetime
    description: str
    notes: str | None
    source_transaction_id: UUID
    destination_transaction_id: UUID
    fee_transaction_id: UUID | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: FxTransfer) -> FxTransferResponse:
        return cls(
            id=entity.id,
            organization_id=entity.organization_id,
            source_account_id=entity.source_account_id,
            destination_account_id=entity.destination_account_id,
            source_amount=f"{entity.source_amount:.2f}",
            source_currency=entity.source_currency,
            destination_amount=f"{entity.destination_amount:.2f}",
            destination_currency=entity.destination_currency,
            effective_exchange_rate=format(entity.effective_exchange_rate, "f"),
            fee_amount=f"{entity.fee_amount:.2f}" if entity.fee_amount is not None else None,
            fee_currency=entity.fee_currency,
            occurred_at=entity.occurred_at,
            description=entity.description,
            notes=entity.notes,
            source_transaction_id=entity.source_transaction_id,
            destination_transaction_id=entity.destination_transaction_id,
            fee_transaction_id=entity.fee_transaction_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
