"""Summary and workpaper schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class MexicoTaxWorkpaperResponse(BaseModel):
    period_id: str
    currency: str
    collected_income: str
    taxable_income: str
    exempt_income: str
    paid_expenses: str
    deductible_expenses: str
    non_deductible_expenses: str
    output_vat: str
    identified_input_vat: str
    creditable_vat: str
    withheld_vat: str
    vat_due: str
    vat_credit_balance: str
    estimated_income_tax: str
    withheld_income_tax: str
    income_tax_due: str
    income_tax_credit: str
    estimated_total_due: str
    quality: dict
    warnings: list[dict] = Field(default_factory=list)
    lines: list[dict] = Field(default_factory=list)
    configuration_version: int
    catalog_version: str
    calculation_engine: str
    calculation_engine_version: str


class MexicoTaxSummaryResponse(BaseModel):
    tax_profile_id: UUID
    period_id: UUID | None
    currency: str
    income_tax_due: Decimal
    vat_due: Decimal
    estimated_total_due: Decimal
    income_tax_reserve_recommended: Decimal
    vat_reserve_recommended: Decimal
    is_stale: bool
    calculated_at: datetime | None
    latest_relevant_change_at: datetime | None
