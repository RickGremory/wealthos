"""Account create schema."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    account_type: str = Field(min_length=1, max_length=30)
    currency: str = Field(min_length=3, max_length=3)
    opening_balance: Decimal = Decimal("0.00")
    opening_balance_date: date | None = None
    institution_name: str | None = Field(default=None, max_length=120)
    last_four: str | None = Field(default=None, min_length=4, max_length=4)
