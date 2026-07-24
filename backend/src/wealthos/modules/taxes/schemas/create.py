"""Tax profile create schema."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class TaxProfileCreate(BaseModel):
    country_code: str = Field(min_length=2, max_length=2)
    taxpayer_type: str
    filing_frequency: str
    currency: str = Field(min_length=3, max_length=3)
    fiscal_year_start_month: int = Field(default=1, ge=1, le=12)
    jurisdiction: str | None = None
    tax_regime: str | None = None
    reserve_account_id: UUID | None = None
