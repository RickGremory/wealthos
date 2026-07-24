"""Transaction collection schema."""

from __future__ import annotations

from pydantic import BaseModel

from wealthos.modules.transactions.schemas.response import TransactionResponse


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    limit: int
    offset: int
