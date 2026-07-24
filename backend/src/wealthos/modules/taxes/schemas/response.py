"""Tax response schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from wealthos.modules.taxes.application.commands.calculate_tax_period import (
    CalculateTaxPeriodResult,
)
from wealthos.modules.taxes.application.views.tax_period_detail import TaxPeriodDetail
from wealthos.modules.taxes.domain.entities.tax_calculation import TaxCalculation
from wealthos.modules.taxes.domain.entities.tax_category_mapping import TaxCategoryMapping
from wealthos.modules.taxes.domain.entities.tax_payment import TaxPayment
from wealthos.modules.taxes.domain.entities.tax_period import TaxPeriod
from wealthos.modules.taxes.domain.entities.tax_profile import TaxProfile
from wealthos.modules.taxes.domain.entities.tax_rule import TaxRule
from wealthos.modules.taxes.domain.entities.tax_transaction_override import (
    TaxTransactionOverride,
)


class TaxProfileResponse(BaseModel):
    id: UUID
    organization_id: UUID
    country_code: str
    jurisdiction: str | None
    taxpayer_type: str
    tax_regime: str | None
    filing_frequency: str
    fiscal_year_start_month: int
    currency: str
    reserve_account_id: UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, profile: TaxProfile) -> TaxProfileResponse:
        return cls(
            id=profile.id,
            organization_id=profile.organization_id,
            country_code=profile.country_code.value,
            jurisdiction=profile.jurisdiction,
            taxpayer_type=profile.taxpayer_type.value,
            tax_regime=profile.tax_regime,
            filing_frequency=profile.filing_frequency.value,
            fiscal_year_start_month=profile.fiscal_year_start_month,
            currency=profile.currency.value,
            reserve_account_id=profile.reserve_account_id,
            is_active=profile.is_active,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )


class TaxProfileListResponse(BaseModel):
    items: list[TaxProfileResponse]
    total: int


class TaxRuleResponse(BaseModel):
    id: UUID
    organization_id: UUID
    tax_profile_id: UUID
    name: str
    tax_type: str
    calculation_method: str
    rate: Decimal | None
    fixed_amount: Decimal | None
    applies_to: str
    tax_inclusion_mode: str
    category_ids: list[UUID]
    priority: int
    is_active: bool
    effective_from: date
    effective_to: date | None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None

    @classmethod
    def from_entity(cls, rule: TaxRule) -> TaxRuleResponse:
        return cls(
            id=rule.id,
            organization_id=rule.organization_id,
            tax_profile_id=rule.tax_profile_id,
            name=rule.name.value,
            tax_type=rule.tax_type.value,
            calculation_method=rule.calculation_method.value,
            rate=rule.rate.value if rule.rate else None,
            fixed_amount=rule.fixed_amount.amount if rule.fixed_amount else None,
            applies_to=rule.applies_to.value,
            tax_inclusion_mode=rule.tax_inclusion_mode.value,
            category_ids=list(rule.category_ids),
            priority=rule.priority,
            is_active=rule.is_active,
            effective_from=rule.effective_from,
            effective_to=rule.effective_to,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            archived_at=rule.archived_at,
        )


class TaxRuleListResponse(BaseModel):
    items: list[TaxRuleResponse]
    total: int


class TaxCalculationLineResponse(BaseModel):
    id: UUID
    tax_rule_id: UUID
    description: str
    taxable_base: Decimal
    rate: Decimal | None
    calculated_amount: Decimal
    currency: str


class TaxCalculationResponse(BaseModel):
    id: UUID
    tax_period_id: UUID
    version: int
    status: str
    gross_income: Decimal
    taxable_income: Decimal
    deductible_expenses: Decimal
    taxable_base: Decimal
    estimated_tax: Decimal
    currency: str
    calculated_at: datetime
    calculated_by_user_id: UUID
    lines: list[TaxCalculationLineResponse]
    paid_amount: Decimal | None = None
    balance: Decimal | None = None

    @classmethod
    def from_entity(
        cls,
        calculation: TaxCalculation,
        *,
        paid_amount: Decimal | None = None,
        balance: Decimal | None = None,
    ) -> TaxCalculationResponse:
        currency = calculation.estimated_tax.currency.value
        balance_value = balance
        if balance_value is None and paid_amount is not None:
            balance_value = max(calculation.estimated_tax.amount - paid_amount, Decimal("0.00"))
        return cls(
            id=calculation.id,
            tax_period_id=calculation.tax_period_id,
            version=calculation.version,
            status=calculation.status.value,
            gross_income=calculation.gross_income.amount,
            taxable_income=calculation.taxable_income.amount,
            deductible_expenses=calculation.deductible_expenses.amount,
            taxable_base=calculation.taxable_base.amount,
            estimated_tax=calculation.estimated_tax.amount,
            currency=currency,
            calculated_at=calculation.calculated_at,
            calculated_by_user_id=calculation.calculated_by_user_id,
            lines=[
                TaxCalculationLineResponse(
                    id=line.id,
                    tax_rule_id=line.tax_rule_id,
                    description=line.description,
                    taxable_base=line.taxable_base.amount,
                    rate=line.rate,
                    calculated_amount=line.calculated_amount.amount,
                    currency=line.calculated_amount.currency.value,
                )
                for line in calculation.lines
            ],
            paid_amount=paid_amount,
            balance=balance_value,
        )

    @classmethod
    def from_calculate_result(cls, result: CalculateTaxPeriodResult) -> TaxCalculationResponse:
        balance = max(result.calculation.estimated_tax.amount - result.paid_amount, Decimal("0.00"))
        return cls.from_entity(
            result.calculation,
            paid_amount=result.paid_amount,
            balance=balance,
        )


class TaxPeriodResponse(BaseModel):
    id: UUID
    organization_id: UUID
    tax_profile_id: UUID
    period_type: str
    date_from: date
    date_to: date
    status: str
    currency: str
    calculated_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    latest_calculation: TaxCalculationResponse | None = None
    paid_amount: Decimal | None = None
    balance: Decimal | None = None

    @classmethod
    def from_entity(cls, period: TaxPeriod) -> TaxPeriodResponse:
        return cls(
            id=period.id,
            organization_id=period.organization_id,
            tax_profile_id=period.tax_profile_id,
            period_type=period.period_type.value,
            date_from=period.date_from,
            date_to=period.date_to,
            status=period.status.value,
            currency=period.currency.value,
            calculated_at=period.calculated_at,
            closed_at=period.closed_at,
            created_at=period.created_at,
            updated_at=period.updated_at,
        )

    @classmethod
    def from_detail(cls, detail: TaxPeriodDetail) -> TaxPeriodResponse:
        base = cls.from_entity(detail.period)
        calc = None
        if detail.latest_calculation is not None:
            calc = TaxCalculationResponse.from_entity(
                detail.latest_calculation,
                paid_amount=detail.paid_amount,
                balance=detail.balance,
            )
        return base.model_copy(
            update={
                "latest_calculation": calc,
                "paid_amount": detail.paid_amount,
                "balance": detail.balance,
            }
        )


class TaxPeriodListResponse(BaseModel):
    items: list[TaxPeriodResponse]
    total: int


class TaxPaymentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    tax_period_id: UUID
    tax_type: str
    transaction_id: UUID
    source_account_id: UUID
    amount: Decimal
    currency: str
    paid_at: datetime
    reference: str | None
    notes: str | None
    idempotency_key: str | None
    created_by_user_id: UUID
    created_at: datetime

    @classmethod
    def from_entity(cls, payment: TaxPayment) -> TaxPaymentResponse:
        return cls(
            id=payment.id,
            organization_id=payment.organization_id,
            tax_period_id=payment.tax_period_id,
            tax_type=payment.tax_type.value,
            transaction_id=payment.transaction_id,
            source_account_id=payment.source_account_id,
            amount=payment.amount.amount,
            currency=payment.amount.currency.value,
            paid_at=payment.paid_at,
            reference=payment.reference,
            notes=payment.notes,
            idempotency_key=payment.idempotency_key,
            created_by_user_id=payment.created_by_user_id,
            created_at=payment.created_at,
        )


class TaxCategoryMappingResponse(BaseModel):
    id: UUID
    category_id: UUID
    tax_treatment: str
    deductibility_percentage: Decimal

    @classmethod
    def from_entity(cls, mapping: TaxCategoryMapping) -> TaxCategoryMappingResponse:
        return cls(
            id=mapping.id,
            category_id=mapping.category_id,
            tax_treatment=mapping.tax_treatment.value,
            deductibility_percentage=mapping.deductibility_percentage.value,
        )


class TaxTransactionOverrideResponse(BaseModel):
    id: UUID
    transaction_id: UUID
    tax_treatment: str
    deductibility_percentage: Decimal
    reason: str | None

    @classmethod
    def from_entity(cls, override: TaxTransactionOverride) -> TaxTransactionOverrideResponse:
        return cls(
            id=override.id,
            transaction_id=override.transaction_id,
            tax_treatment=override.tax_treatment.value,
            deductibility_percentage=override.deductibility_percentage.value,
            reason=override.reason,
        )
