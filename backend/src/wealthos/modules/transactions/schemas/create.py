"""Transaction create schemas (discriminated union)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TransactionSourceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["recurring_occurrence"]
    occurrence_key: str = Field(min_length=10, max_length=120)
    related_resource_type: Literal["recurring_rule"] | None = "recurring_rule"
    related_resource_id: UUID | None = None

    @model_validator(mode="after")
    def _key_prefix(self) -> TransactionSourceCreate:
        if not self.occurrence_key.startswith("recurring:"):
            raise ValueError("occurrence_key must start with 'recurring:'.")
        return self


class _BaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    description: str = Field(min_length=2, max_length=200)
    occurred_at: datetime
    notes: str | None = None
    source: TransactionSourceCreate | None = None


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
