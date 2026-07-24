"""Debt update schema."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DebtUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=120)
    annual_interest_rate: Decimal | None = Field(default=None, ge=0)
    minimum_payment: Decimal | None = Field(default=None, gt=0)
    maturity_date: date | None = None
    payment_day: int | None = Field(default=None, ge=1, le=31)
    statement_day: int | None = Field(default=None, ge=1, le=31)
    notes: str | None = None

    @model_validator(mode="after")
    def reject_empty(self) -> DebtUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self
