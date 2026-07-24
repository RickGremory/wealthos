"""Tax profile and rule update schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TaxProfileUpdate(BaseModel):
    jurisdiction: str | None = None
    tax_regime: str | None = None
    filing_frequency: str | None = None
    fiscal_year_start_month: int | None = Field(default=None, ge=1, le=12)
    reserve_account_id: UUID | None = None
    clear_reserve_account: bool = False


class TaxRuleCreate(BaseModel):
    tax_profile_id: UUID
    name: str = Field(min_length=1, max_length=120)
    tax_type: str
    calculation_method: str
    applies_to: str
    effective_from: date
    rate: Decimal | None = None
    fixed_amount: Decimal | None = None
    tax_inclusion_mode: str = "exclusive"
    category_ids: list[UUID] = Field(default_factory=list)
    priority: int = 100
    effective_to: date | None = None


class TaxRuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    rate: Decimal | None = None
    fixed_amount: Decimal | None = None
    priority: int | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    clear_effective_to: bool = False
    category_ids: list[UUID] | None = None


class TaxCategoryMappingCreate(BaseModel):
    category_id: UUID
    tax_treatment: str
    deductibility_percentage: Decimal = Field(default=Decimal("100"), ge=0, le=100)


class TaxTransactionOverrideCreate(BaseModel):
    transaction_id: UUID
    tax_treatment: str
    deductibility_percentage: Decimal = Field(default=Decimal("100"), ge=0, le=100)
    reason: str | None = None


class TaxPaymentCreate(BaseModel):
    source_account_id: UUID
    amount: Decimal = Field(gt=0)
    tax_type: str
    paid_at: datetime
    reference: str | None = None
    notes: str | None = None
