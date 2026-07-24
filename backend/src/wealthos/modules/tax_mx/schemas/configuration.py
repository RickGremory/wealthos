"""Pydantic schemas for Mexico tax configuration and responses."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from wealthos.modules.tax_mx.domain.entities.mexico_tax_configuration import (
    MexicoTaxConfiguration,
)


class IncomeTaxEstimationPayload(BaseModel):
    method: str = "configured_rate"
    base: str = "gross_taxable_income"
    rate: Decimal


class MexicoTaxConfigurationCreate(BaseModel):
    rfc: str
    person_type: str
    tax_regime_code: str
    vat_enabled: bool = True
    income_tax_enabled: bool = True
    default_vat_rate: Decimal | None = None
    income_tax_estimation: IncomeTaxEstimationPayload | None = None
    requires_invoice_evidence: bool = True
    effective_from: date
    tax_profile_id: UUID | None = None


class MexicoTaxConfigurationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rfc: str
    person_type: str
    tax_regime_code: str
    vat_enabled: bool = True
    income_tax_enabled: bool = True
    default_vat_rate: Decimal | None = None
    income_tax_estimation: IncomeTaxEstimationPayload | None = None
    requires_invoice_evidence: bool = True
    effective_from: date


class MexicoTaxConfigurationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    tax_profile_id: UUID
    version: int
    rfc: str
    person_type: str
    tax_regime_code: str
    vat_enabled: bool
    income_tax_enabled: bool
    default_vat_rate: Decimal | None
    income_tax_estimation_method: str | None
    income_tax_estimation_base: str | None
    income_tax_estimation_rate: Decimal | None
    cash_flow_basis: bool
    requires_invoice_evidence: bool
    effective_from: date
    effective_to: date | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: MexicoTaxConfiguration) -> MexicoTaxConfigurationResponse:
        return cls(
            id=entity.id,
            organization_id=entity.organization_id,
            tax_profile_id=entity.tax_profile_id,
            version=entity.version,
            rfc=entity.rfc.value,
            person_type=entity.person_type.value,
            tax_regime_code=entity.tax_regime_code,
            vat_enabled=entity.vat_enabled,
            income_tax_enabled=entity.income_tax_enabled,
            default_vat_rate=(entity.default_vat_rate.value if entity.default_vat_rate else None),
            income_tax_estimation_method=(
                entity.income_tax_estimation_method.value
                if entity.income_tax_estimation_method
                else None
            ),
            income_tax_estimation_base=(
                entity.income_tax_estimation_base.value
                if entity.income_tax_estimation_base
                else None
            ),
            income_tax_estimation_rate=(
                entity.income_tax_estimation_rate.value
                if entity.income_tax_estimation_rate
                else None
            ),
            cash_flow_basis=entity.cash_flow_basis,
            requires_invoice_evidence=entity.requires_invoice_evidence,
            effective_from=entity.effective_from,
            effective_to=entity.effective_to,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class MexicoCategoryMappingCreate(BaseModel):
    tax_profile_id: UUID
    category_id: UUID
    vat_treatment: str
    income_treatment: str | None = None
    expense_treatment: str | None = None
    deductibility_percentage: Decimal = Decimal("100")
    vat_creditable_percentage: Decimal = Decimal("100")
    requires_cfdi: bool = False
    requires_payment_evidence: bool = False


class MexicoCategoryMappingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vat_treatment: str | None = None
    income_treatment: str | None = None
    expense_treatment: str | None = None
    deductibility_percentage: Decimal | None = None
    vat_creditable_percentage: Decimal | None = None
    requires_cfdi: bool | None = None
    requires_payment_evidence: bool | None = None


class MexicoCategoryMappingResponse(BaseModel):
    id: UUID
    tax_profile_id: UUID
    category_id: UUID
    income_treatment: str | None
    expense_treatment: str | None
    vat_treatment: str
    deductibility_percentage: Decimal
    vat_creditable_percentage: Decimal
    requires_cfdi: bool
    requires_payment_evidence: bool


class MexicoClassificationCreate(BaseModel):
    tax_profile_id: UUID
    vat_treatment: str
    income_treatment: str | None = None
    expense_treatment: str | None = None
    deductibility_percentage: Decimal = Decimal("100")
    vat_creditable_percentage: Decimal = Decimal("100")
    requires_cfdi: bool = False
    reason: str | None = None


class MexicoWorkpaperResponse(BaseModel):
    period_id: UUID
    currency: str
    income: dict
    expenses: dict
    vat: dict
    income_tax: dict
    estimated_total_due: Decimal
    quality: dict
    warnings: list[dict] = Field(default_factory=list)
    is_stale: bool = False
    version: int | None = None


class MexicoTaxSummaryResponse(BaseModel):
    currency: str
    income_tax: dict
    vat: dict
    total: dict


class UnclassifiedTransactionItem(BaseModel):
    transaction_id: UUID
    description: str
    occurred_at: date
    amount: Decimal
    currency: str
    category: dict | None
    missing: list[str]


class UnclassifiedTransactionListResponse(BaseModel):
    items: list[UnclassifiedTransactionItem]
    total: int


class CatalogListResponse(BaseModel):
    catalog_version: str
    catalogs: dict[str, list[dict]]
