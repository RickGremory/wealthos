"""Debt create schema."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

DebtTypeLiteral = Literal[
    "credit_card",
    "personal_loan",
    "auto_loan",
    "mortgage",
    "student_loan",
    "tax_debt",
    "line_of_credit",
    "other",
]


class DebtCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    account_id: UUID
    name: str = Field(min_length=2, max_length=120)
    debt_type: DebtTypeLiteral
    annual_interest_rate: Decimal = Field(ge=0)
    minimum_payment: Decimal = Field(gt=0)
    original_principal: Decimal | None = Field(default=None, ge=0)
    opened_at: date | None = None
    maturity_date: date | None = None
    payment_day: int | None = Field(default=None, ge=1, le=31)
    statement_day: int | None = Field(default=None, ge=1, le=31)
    notes: str | None = Field(default=None, max_length=2000)
