"""Recent transactions response schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from wealthos.modules.dashboard.application.views.recent_transaction import (
    RecentTransactionView,
)


class NamedRefResponse(BaseModel):
    id: UUID
    name: str


class RecentTransactionResponse(BaseModel):
    id: UUID
    transaction_type: str
    description: str
    category: NamedRefResponse | None
    occurred_at: datetime
    status: str
    amount: Decimal
    currency: str
    account: NamedRefResponse | None = None
    source_account: NamedRefResponse | None = None
    destination_account: NamedRefResponse | None = None


class RecentTransactionsResponse(BaseModel):
    """Recent movements with positive amounts; type conveys direction."""

    items: list[RecentTransactionResponse]
    total: int

    @classmethod
    def from_views(
        cls,
        items: list[RecentTransactionView],
    ) -> RecentTransactionsResponse:
        return cls(
            items=[
                RecentTransactionResponse(
                    id=item.id,
                    transaction_type=item.transaction_type,
                    description=item.description,
                    category=(
                        NamedRefResponse(id=item.category.id, name=item.category.name)
                        if item.category
                        else None
                    ),
                    occurred_at=item.occurred_at,
                    status=item.status,
                    amount=item.amount,
                    currency=item.currency,
                    account=(
                        NamedRefResponse(id=item.account.id, name=item.account.name)
                        if item.account
                        else None
                    ),
                    source_account=(
                        NamedRefResponse(
                            id=item.source_account.id,
                            name=item.source_account.name,
                        )
                        if item.source_account
                        else None
                    ),
                    destination_account=(
                        NamedRefResponse(
                            id=item.destination_account.id,
                            name=item.destination_account.name,
                        )
                        if item.destination_account
                        else None
                    ),
                )
                for item in items
            ],
            total=len(items),
        )
