"""CalculateMexicoTaxPeriod — specialized MX workpaper + core TaxCalculation snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.tax_mx.application.services.mexico_tax_calculation_service import (
    ClassificationBundle,
    MexicoMonthlyTaxWorkpaper,
    MexicoTaxCalculationService,
)
from wealthos.modules.tax_mx.domain.exceptions import (
    MexicoTaxConfigurationNotFound,
    MexicoTaxPeriodClosed,
    MexicoTaxPeriodNotFound,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_category_mapping_repository import (
    MexicoTaxCategoryMappingRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_configuration_repository import (
    MexicoTaxConfigurationRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_details_repository import (
    MexicoTaxDetailsRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_read_repository import (
    MexicoTaxReadRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_snapshot_repository import (
    MexicoTaxSnapshotRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_transaction_override_repository import (
    MexicoTaxTransactionOverrideRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_withholding_repository import (
    MexicoTaxWithholdingRepository,
)
from wealthos.modules.tax_mx.domain.repositories.tax_evidence_repository import (
    TaxEvidenceRepository,
)
from wealthos.modules.taxes.domain.entities.tax_calculation import TaxCalculation
from wealthos.modules.taxes.domain.repositories.tax_calculation_repository import (
    TaxCalculationRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_period_repository import (
    TaxPeriodRepository,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class CalculateMexicoTaxPeriodResult:
    workpaper: MexicoMonthlyTaxWorkpaper
    tax_calculation_id: UUID
    version: int


class CalculateMexicoTaxPeriodCommand:
    def __init__(
        self,
        periods: TaxPeriodRepository,
        configurations: MexicoTaxConfigurationRepository,
        mappings: MexicoTaxCategoryMappingRepository,
        overrides: MexicoTaxTransactionOverrideRepository,
        details: MexicoTaxDetailsRepository,
        evidence: TaxEvidenceRepository,
        withholdings: MexicoTaxWithholdingRepository,
        read: MexicoTaxReadRepository,
        calculations: TaxCalculationRepository,
        snapshots: MexicoTaxSnapshotRepository,
        calculator: MexicoTaxCalculationService | None = None,
    ) -> None:
        self._periods = periods
        self._configurations = configurations
        self._mappings = mappings
        self._overrides = overrides
        self._details = details
        self._evidence = evidence
        self._withholdings = withholdings
        self._read = read
        self._calculations = calculations
        self._snapshots = snapshots
        self._calculator = calculator or MexicoTaxCalculationService()

    def execute(
        self,
        organization_id: UUID,
        period_id: UUID,
        performed_by_user_id: UUID,
    ) -> CalculateMexicoTaxPeriodResult:
        period = self._periods.lock_for_update(organization_id, period_id)
        if period is None:
            raise MexicoTaxPeriodNotFound("Tax period not found.")
        if period.status.value == "closed":
            raise MexicoTaxPeriodClosed("Cannot recalculate a closed tax period.")

        configuration = self._configurations.get_applicable(period.tax_profile_id, period.date_to)
        if configuration is None:
            raise MexicoTaxConfigurationNotFound(
                "No Mexico tax configuration applicable for this period."
            )

        transactions = self._read.get_period_transactions(
            organization_id,
            date_from=period.date_from,
            date_to=period.date_to,
            currency=period.currency.value,
        )
        tx_ids = [tx.transaction_id for tx in transactions]
        mappings = {
            item.category_id: item
            for item in self._mappings.list_by_profile(organization_id, period.tax_profile_id)
        }
        overrides = {
            item.transaction_id: item
            for item in self._overrides.list_by_profile(organization_id, period.tax_profile_id)
        }
        details = {
            item.transaction_id: item
            for item in self._details.list_by_transactions(organization_id, tx_ids)
        }
        evidence_status = self._evidence.latest_status_by_transactions(organization_id, tx_ids)
        withholdings = self._withholdings.list_by_transactions(organization_id, tx_ids)
        wit_isr: dict[UUID, Decimal] = {}
        wit_vat: dict[UUID, Decimal] = {}
        for item in withholdings:
            if item.withholding_type.value == "income_tax":
                wit_isr[item.transaction_id] = (
                    wit_isr.get(item.transaction_id, Decimal("0")) + item.amount.amount
                )
            elif item.withholding_type.value == "vat":
                wit_vat[item.transaction_id] = (
                    wit_vat.get(item.transaction_id, Decimal("0")) + item.amount.amount
                )

        bundle = ClassificationBundle(
            mappings=mappings,
            overrides=overrides,
            details=details,
            evidence_status_by_tx=evidence_status,
            withholdings_income_tax=wit_isr,
            withholdings_vat=wit_vat,
        )
        workpaper = self._calculator.calculate(
            period_id=period.id,
            configuration=configuration,
            transactions=transactions,
            bundle=bundle,
            currency=period.currency.value,
        )

        self._calculations.supersede_completed(period.id)
        version = self._calculations.get_next_version(period.id)
        calc_id = uuid4()
        currency = period.currency.value
        calculation = TaxCalculation.create(
            organization_id=organization_id,
            tax_period_id=period.id,
            version=version,
            gross_income=Money(workpaper.collected_income, currency),
            taxable_income=Money(workpaper.taxable_income, currency),
            deductible_expenses=Money(workpaper.deductible_expenses, currency),
            taxable_base=Money(
                max(workpaper.taxable_income - workpaper.deductible_expenses, Decimal("0")),
                currency,
            ),
            estimated_tax=Money(workpaper.estimated_total_due, currency),
            calculated_by_user_id=performed_by_user_id,
            lines=[],
            calculation_id=calc_id,
        )
        stored = self._calculations.add(calculation)
        period.mark_calculated()
        self._periods.save(period)

        cutoff = self._read.latest_relevant_change_at(
            organization_id,
            date_from=period.date_from,
            date_to=period.date_to,
        ) or datetime.now(UTC)
        payload = workpaper_to_json(workpaper)
        self._snapshots.add(
            organization_id=organization_id,
            tax_calculation_id=stored.id,
            configuration_version=workpaper.configuration_version,
            catalog_version=workpaper.catalog_version,
            calculation_engine=workpaper.calculation_engine,
            calculation_engine_version=workpaper.calculation_engine_version,
            transaction_cutoff_at=cutoff,
            workpaper_json=payload,
        )
        return CalculateMexicoTaxPeriodResult(
            workpaper=workpaper,
            tax_calculation_id=stored.id,
            version=stored.version,
        )


def workpaper_to_json(workpaper: MexicoMonthlyTaxWorkpaper) -> dict:
    return {
        "period_id": str(workpaper.period_id),
        "currency": workpaper.currency,
        "collected_income": str(workpaper.collected_income),
        "taxable_income": str(workpaper.taxable_income),
        "exempt_income": str(workpaper.exempt_income),
        "paid_expenses": str(workpaper.paid_expenses),
        "deductible_expenses": str(workpaper.deductible_expenses),
        "non_deductible_expenses": str(workpaper.non_deductible_expenses),
        "output_vat": str(workpaper.output_vat),
        "identified_input_vat": str(workpaper.identified_input_vat),
        "creditable_vat": str(workpaper.creditable_vat),
        "withheld_vat": str(workpaper.withheld_vat),
        "vat_due": str(workpaper.vat_due),
        "vat_credit_balance": str(workpaper.vat_credit_balance),
        "estimated_income_tax": str(workpaper.estimated_income_tax),
        "withheld_income_tax": str(workpaper.withheld_income_tax),
        "income_tax_due": str(workpaper.income_tax_due),
        "income_tax_credit": str(workpaper.income_tax_credit),
        "estimated_total_due": str(workpaper.estimated_total_due),
        "quality": {
            "total_transactions": workpaper.quality.total_transactions,
            "classified_transactions": workpaper.quality.classified_transactions,
            "unclassified_transactions": workpaper.quality.unclassified_transactions,
            "transactions_requiring_evidence": workpaper.quality.transactions_requiring_evidence,
            "missing_evidence": workpaper.quality.missing_evidence,
            "mismatched_evidence": workpaper.quality.mismatched_evidence,
            "completeness_percentage": str(workpaper.quality.completeness_percentage),
        },
        "warnings": [
            {
                "code": warning.code,
                "message": warning.message,
                "transaction_id": (str(warning.transaction_id) if warning.transaction_id else None),
            }
            for warning in workpaper.warnings
        ],
        "lines": list(workpaper.lines),
        "configuration_version": workpaper.configuration_version,
        "catalog_version": workpaper.catalog_version,
        "calculation_engine": workpaper.calculation_engine,
        "calculation_engine_version": workpaper.calculation_engine_version,
    }
