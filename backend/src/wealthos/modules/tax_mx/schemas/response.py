"""Response schemas for tax_mx."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from wealthos.modules.tax_mx.domain.entities.mexico_tax_classification import (
    MexicoTaxCategoryMapping,
    MexicoTaxTransactionOverride,
)
from wealthos.modules.tax_mx.domain.entities.mexico_tax_configuration import (
    MexicoTaxConfiguration,
)
from wealthos.modules.tax_mx.domain.entities.tax_evidence import MexicoTransactionTaxDetails


class MexicoTaxConfigurationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class MexicoTaxCategoryMappingResponse(BaseModel):
    id: UUID
    organization_id: UUID
    tax_profile_id: UUID
    category_id: UUID
    income_treatment: str | None
    expense_treatment: str | None
    vat_treatment: str
    deductibility_percentage: Decimal
    vat_creditable_percentage: Decimal
    requires_cfdi: bool
    requires_payment_evidence: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: MexicoTaxCategoryMapping) -> MexicoTaxCategoryMappingResponse:
        return cls(
            id=entity.id,
            organization_id=entity.organization_id,
            tax_profile_id=entity.tax_profile_id,
            category_id=entity.category_id,
            income_treatment=(entity.income_treatment.value if entity.income_treatment else None),
            expense_treatment=(
                entity.expense_treatment.value if entity.expense_treatment else None
            ),
            vat_treatment=entity.vat_treatment.value,
            deductibility_percentage=entity.deductibility_percentage.value,
            vat_creditable_percentage=entity.vat_creditable_percentage.value,
            requires_cfdi=entity.requires_cfdi,
            requires_payment_evidence=entity.requires_payment_evidence,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class MexicoTaxTransactionOverrideResponse(BaseModel):
    id: UUID
    organization_id: UUID
    tax_profile_id: UUID
    transaction_id: UUID
    income_treatment: str | None
    expense_treatment: str | None
    vat_treatment: str
    deductibility_percentage: Decimal
    vat_creditable_percentage: Decimal
    requires_cfdi: bool
    reason: str | None
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(
        cls, entity: MexicoTaxTransactionOverride
    ) -> MexicoTaxTransactionOverrideResponse:
        return cls(
            id=entity.id,
            organization_id=entity.organization_id,
            tax_profile_id=entity.tax_profile_id,
            transaction_id=entity.transaction_id,
            income_treatment=(entity.income_treatment.value if entity.income_treatment else None),
            expense_treatment=(
                entity.expense_treatment.value if entity.expense_treatment else None
            ),
            vat_treatment=entity.vat_treatment.value,
            deductibility_percentage=entity.deductibility_percentage.value,
            vat_creditable_percentage=entity.vat_creditable_percentage.value,
            requires_cfdi=entity.requires_cfdi,
            reason=entity.reason,
            created_by_user_id=entity.created_by_user_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class MexicoTransactionTaxDetailsResponse(BaseModel):
    id: UUID
    organization_id: UUID
    transaction_id: UUID
    subtotal: Decimal
    vat_amount: Decimal
    withheld_income_tax: Decimal
    withheld_vat: Decimal
    other_taxes: Decimal
    total: Decimal
    currency: str
    calculation_source: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(
        cls, entity: MexicoTransactionTaxDetails
    ) -> MexicoTransactionTaxDetailsResponse:
        return cls(
            id=entity.id,
            organization_id=entity.organization_id,
            transaction_id=entity.transaction_id,
            subtotal=entity.subtotal.amount,
            vat_amount=entity.vat_amount.amount,
            withheld_income_tax=entity.withheld_income_tax.amount,
            withheld_vat=entity.withheld_vat.amount,
            other_taxes=entity.other_taxes.amount,
            total=entity.total.amount,
            currency=entity.total.currency.value,
            calculation_source=entity.calculation_source.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class MexicoTaxCatalogEntryResponse(BaseModel):
    code: str
    name: str
    catalog_name: str
    catalog_version: str
    person_type: str | None = None
    rate: Decimal | None = None
    metadata_json: dict | None = None
    valid_from: date
    valid_to: date | None = None
    source_reference: str | None = None


class MexicoTaxCatalogListResponse(BaseModel):
    tax_regimes: list[MexicoTaxCatalogEntryResponse]
    vat_rates: list[MexicoTaxCatalogEntryResponse]
    withholding_types: list[MexicoTaxCatalogEntryResponse]
