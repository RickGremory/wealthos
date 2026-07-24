"""Create schemas for tax_mx."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class MexicoTaxConfigurationCreate(BaseModel):
    tax_profile_id: str
    rfc: str = Field(min_length=12, max_length=13)
    person_type: str
    tax_regime_code: str
    effective_from: date
    vat_enabled: bool = True
    income_tax_enabled: bool = True
    default_vat_rate: Decimal | None = Decimal("16")
    income_tax_estimation_method: str | None = "configured_rate"
    income_tax_estimation_base: str | None = "gross_taxable_income"
    income_tax_estimation_rate: Decimal | None = None
    requires_invoice_evidence: bool = True


class MexicoTaxConfigurationRevise(BaseModel):
    effective_from: date
    rfc: str | None = None
    person_type: str | None = None
    tax_regime_code: str | None = None
    vat_enabled: bool | None = None
    income_tax_enabled: bool | None = None
    default_vat_rate: Decimal | None = None
    income_tax_estimation_method: str | None = None
    income_tax_estimation_base: str | None = None
    income_tax_estimation_rate: Decimal | None = None
    requires_invoice_evidence: bool | None = None


class MexicoTaxCategoryMappingCreate(BaseModel):
    tax_profile_id: str
    category_id: str
    vat_treatment: str
    income_treatment: str | None = None
    expense_treatment: str | None = None
    deductibility_percentage: Decimal = Decimal("100")
    vat_creditable_percentage: Decimal = Decimal("100")
    requires_cfdi: bool = False
    requires_payment_evidence: bool = False


class MexicoTaxCategoryMappingUpdate(BaseModel):
    vat_treatment: str | None = None
    income_treatment: str | None = None
    expense_treatment: str | None = None
    deductibility_percentage: Decimal | None = None
    vat_creditable_percentage: Decimal | None = None
    requires_cfdi: bool | None = None
    requires_payment_evidence: bool | None = None
    clear_income_treatment: bool = False
    clear_expense_treatment: bool = False


class MexicoTaxTransactionClassificationCreate(BaseModel):
    tax_profile_id: str
    vat_treatment: str
    income_treatment: str | None = None
    expense_treatment: str | None = None
    deductibility_percentage: Decimal = Decimal("100")
    vat_creditable_percentage: Decimal = Decimal("100")
    requires_cfdi: bool = False
    reason: str | None = None


class MexicoTransactionTaxDetailsCreate(BaseModel):
    subtotal: Decimal
    vat_amount: Decimal
    total: Decimal
    currency: str = "MXN"
    withheld_income_tax: Decimal = Decimal("0")
    withheld_vat: Decimal = Decimal("0")
    other_taxes: Decimal = Decimal("0")
    calculation_source: str = "manual"
