"""Debt create schema."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

DebtTypeLiteral = Literal[
    "credit_card",
    "mortgage",
    "auto_loan",
    "personal_loan",
    "business_loan",
    "student_loan",
    "line_of_credit",
    "family_loan",
    "installment_plan",
    "other",
]

DebtPriorityLiteral = Literal["high", "medium", "low"]


class DebtCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    account_id: UUID
    name: str = Field(min_length=2, max_length=120)
    debt_type: DebtTypeLiteral
    creditor: str | None = Field(default=None, max_length=120)
    priority: DebtPriorityLiteral = "medium"
    interest_rate: Decimal | None = Field(default=None, ge=0)
    minimum_payment: Decimal | None = Field(default=None, gt=0)
    scheduled_payment: Decimal | None = Field(default=None, gt=0)
    credit_limit: Decimal | None = Field(default=None, ge=0)
    original_amount: Decimal | None = Field(default=None, ge=0)
    maturity_date: date | None = None
    due_day: int | None = Field(default=None, ge=1, le=31)
    statement_day: int | None = Field(default=None, ge=1, le=31)
    notes: str | None = Field(default=None, max_length=2000)
