"""Debt update schema."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DebtPriorityLiteral = Literal["high", "medium", "low"]


class DebtUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=120)
    creditor: str | None = Field(default=None, max_length=120)
    priority: DebtPriorityLiteral | None = None
    interest_rate: Decimal | None = Field(default=None, ge=0)
    minimum_payment: Decimal | None = Field(default=None, gt=0)
    scheduled_payment: Decimal | None = Field(default=None, gt=0)
    credit_limit: Decimal | None = Field(default=None, ge=0)
    maturity_date: date | None = None
    due_day: int | None = Field(default=None, ge=1, le=31)
    statement_day: int | None = Field(default=None, ge=1, le=31)
    notes: str | None = None
    version: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def reject_empty(self) -> DebtUpdate:
        # version alone is not a meaningful update
        meaningful = self.model_fields_set - {"version"}
        if not meaningful:
            raise ValueError("At least one field must be provided.")
        return self
