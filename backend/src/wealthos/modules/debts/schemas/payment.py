"""Debt payment create schema."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DebtPaymentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_account_id: UUID
    amount: Decimal = Field(gt=0)
    occurred_at: datetime
    description: str | None = Field(default=None, max_length=200)
    principal_amount: Decimal | None = Field(default=None, ge=0)
    interest_amount: Decimal | None = Field(default=None, ge=0)
