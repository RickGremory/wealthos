"""MexicoTaxConfiguration — versioned Mexican fiscal setup for a tax profile."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.tax_mx.domain.exceptions import (
    CashFlowBasisRequired,
    InvalidMexicoTaxConfiguration,
)
from wealthos.modules.tax_mx.domain.value_objects.estimation import (
    IncomeTaxEstimationBase,
    IncomeTaxEstimationMethod,
)
from wealthos.modules.tax_mx.domain.value_objects.mexico_person_type import MexicoPersonType
from wealthos.modules.tax_mx.domain.value_objects.rfc import RFC
from wealthos.modules.taxes.domain.value_objects.percentage import Percentage


@dataclass(slots=True)
class MexicoTaxConfiguration:
    id: UUID
    organization_id: UUID
    tax_profile_id: UUID
    version: int
    rfc: RFC
    person_type: MexicoPersonType
    tax_regime_code: str
    vat_enabled: bool
    income_tax_enabled: bool
    default_vat_rate: Percentage | None
    income_tax_estimation_method: IncomeTaxEstimationMethod | None
    income_tax_estimation_base: IncomeTaxEstimationBase | None
    income_tax_estimation_rate: Percentage | None
    cash_flow_basis: bool
    requires_invoice_evidence: bool
    effective_from: date
    effective_to: date | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        tax_profile_id: UUID,
        version: int,
        rfc: str,
        person_type: str,
        tax_regime_code: str,
        vat_enabled: bool,
        income_tax_enabled: bool,
        effective_from: date,
        default_vat_rate: Decimal | None = None,
        income_tax_estimation_method: str | None = None,
        income_tax_estimation_base: str | None = None,
        income_tax_estimation_rate: Decimal | None = None,
        cash_flow_basis: bool = True,
        requires_invoice_evidence: bool = True,
        effective_to: date | None = None,
        configuration_id: UUID | None = None,
    ) -> MexicoTaxConfiguration:
        if not cash_flow_basis:
            raise CashFlowBasisRequired("V1 requires cash_flow_basis=true.")
        if not vat_enabled and not income_tax_enabled:
            raise InvalidMexicoTaxConfiguration("At least one tax must be enabled.")
        if effective_to is not None and effective_to < effective_from:
            raise InvalidMexicoTaxConfiguration("effective_to cannot precede effective_from.")
        if vat_enabled and default_vat_rate is None:
            raise InvalidMexicoTaxConfiguration("VAT enabled requires default_vat_rate.")
        if income_tax_enabled:
            if income_tax_estimation_method is None or income_tax_estimation_rate is None:
                raise InvalidMexicoTaxConfiguration(
                    "Income tax enabled requires estimation method and rate."
                )
            if income_tax_estimation_base is None:
                raise InvalidMexicoTaxConfiguration("Income tax enabled requires estimation base.")

        now = datetime.now(UTC)
        return cls(
            id=configuration_id or uuid4(),
            organization_id=organization_id,
            tax_profile_id=tax_profile_id,
            version=version,
            rfc=RFC(rfc),
            person_type=MexicoPersonType(person_type),
            tax_regime_code=tax_regime_code.strip(),
            vat_enabled=vat_enabled,
            income_tax_enabled=income_tax_enabled,
            default_vat_rate=Percentage(default_vat_rate) if default_vat_rate is not None else None,
            income_tax_estimation_method=(
                IncomeTaxEstimationMethod(income_tax_estimation_method)
                if income_tax_estimation_method
                else None
            ),
            income_tax_estimation_base=(
                IncomeTaxEstimationBase(income_tax_estimation_base)
                if income_tax_estimation_base
                else None
            ),
            income_tax_estimation_rate=(
                Percentage(income_tax_estimation_rate)
                if income_tax_estimation_rate is not None
                else None
            ),
            cash_flow_basis=True,
            requires_invoice_evidence=requires_invoice_evidence,
            effective_from=effective_from,
            effective_to=effective_to,
            created_at=now,
            updated_at=now,
        )

    def close(self, effective_to: date) -> None:
        if self.effective_to is not None:
            raise InvalidMexicoTaxConfiguration("Configuration already closed.")
        if effective_to < self.effective_from:
            raise InvalidMexicoTaxConfiguration("effective_to cannot precede effective_from.")
        self.effective_to = effective_to
        self.updated_at = datetime.now(UTC)

    def is_applicable_on(self, target: date) -> bool:
        if target < self.effective_from:
            return False
        if self.effective_to is not None and target > self.effective_to:
            return False
        return True
