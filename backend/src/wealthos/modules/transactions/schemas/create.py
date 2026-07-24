"""Transaction create schemas (discriminated union)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _BaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    description: str = Field(min_length=2, max_length=200)
    occurred_at: datetime
    notes: str | None = None


class IncomeTransactionCreate(_BaseCreate):
    transaction_type: Literal["income"]
    account_id: UUID
    category_id: UUID
    amount: Decimal = Field(gt=0)


class ExpenseTransactionCreate(_BaseCreate):
    transaction_type: Literal["expense"]
    account_id: UUID
    category_id: UUID
    amount: Decimal = Field(gt=0)


class TransferTransactionCreate(_BaseCreate):
    transaction_type: Literal["transfer"]
    source_account_id: UUID
    destination_account_id: UUID
    amount: Decimal = Field(gt=0)


class AdjustmentTransactionCreate(_BaseCreate):
    transaction_type: Literal["adjustment"]
    account_id: UUID
    amount: Decimal
    category_id: UUID | None = None


TransactionCreate = Annotated[
    IncomeTransactionCreate
    | ExpenseTransactionCreate
    | TransferTransactionCreate
    | AdjustmentTransactionCreate,
    Field(discriminator="transaction_type"),
]
