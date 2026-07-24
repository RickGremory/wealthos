"""Unclassified transaction schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from wealthos.modules.tax_mx.application.services.mexico_tax_calculation_service import (
    MexicoTaxTransactionView,
)


class UnclassifiedTransactionItem(BaseModel):
    transaction_id: UUID
    transaction_type: str
    status: str
    occurred_on: date
    amount: Decimal
    currency: str
    category_id: UUID | None
    description: str

    @classmethod
    def from_view(cls, view: MexicoTaxTransactionView) -> UnclassifiedTransactionItem:
        return cls(
            transaction_id=view.transaction_id,
            transaction_type=view.transaction_type,
            status=view.status,
            occurred_on=view.occurred_on,
            amount=view.amount,
            currency=view.currency,
            category_id=view.category_id,
            description=view.description,
        )


class UnclassifiedTransactionListResponse(BaseModel):
    items: list[UnclassifiedTransactionItem]
    total: int
