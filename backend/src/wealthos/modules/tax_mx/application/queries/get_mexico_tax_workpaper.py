"""GetMexicoTaxWorkpaper query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.tax_mx.application.commands.calculate_mexico_tax_period import (
    workpaper_to_json,
)
from wealthos.modules.tax_mx.application.services.classification_bundle_builder import (
    build_mexico_classification_bundle,
)
from wealthos.modules.tax_mx.application.services.mexico_tax_calculation_service import (
    MexicoTaxCalculationService,
)
from wealthos.modules.tax_mx.domain.exceptions import (
    MexicoTaxConfigurationNotFound,
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
from wealthos.modules.taxes.domain.repositories.tax_period_repository import TaxPeriodRepository


class GetMexicoTaxWorkpaperQuery:
    def __init__(
        self,
        periods: TaxPeriodRepository,
        configurations: MexicoTaxConfigurationRepository,
        snapshots: MexicoTaxSnapshotRepository,
        mappings: MexicoTaxCategoryMappingRepository,
        overrides: MexicoTaxTransactionOverrideRepository,
        details: MexicoTaxDetailsRepository,
        evidence: TaxEvidenceRepository,
        withholdings: MexicoTaxWithholdingRepository,
        read: MexicoTaxReadRepository,
        calculator: MexicoTaxCalculationService | None = None,
    ) -> None:
        self._periods = periods
        self._configurations = configurations
        self._snapshots = snapshots
        self._mappings = mappings
        self._overrides = overrides
        self._details = details
        self._evidence = evidence
        self._withholdings = withholdings
        self._read = read
        self._calculator = calculator or MexicoTaxCalculationService()

    def execute(
        self,
        organization_id: UUID,
        period_id: UUID,
        *,
        recompute: bool = False,
    ) -> dict:
        period = self._periods.get_by_id(organization_id, period_id)
        if period is None:
            raise MexicoTaxPeriodNotFound("Tax period not found.")

        if not recompute:
            snapshot = self._snapshots.get_latest_for_period(organization_id, period_id)
            if snapshot is not None:
                return snapshot["workpaper_json"]

        configuration = self._configurations.get_applicable(
            period.tax_profile_id,
            period.date_to,
        )
        if configuration is None:
            raise MexicoTaxConfigurationNotFound(
                "No Mexico tax configuration applies to this period."
            )

        transactions = self._read.get_period_transactions(
            organization_id,
            date_from=period.date_from,
            date_to=period.date_to,
            currency=period.currency.value,
        )
        tx_ids = [tx.transaction_id for tx in transactions]
        bundle = build_mexico_classification_bundle(
            organization_id=organization_id,
            tax_profile_id=period.tax_profile_id,
            transaction_ids=tx_ids,
            mappings=self._mappings,
            overrides=self._overrides,
            details=self._details,
            evidence=self._evidence,
            withholdings=self._withholdings,
        )
        workpaper = self._calculator.calculate(
            period_id=period.id,
            configuration=configuration,
            transactions=transactions,
            bundle=bundle,
            currency=period.currency.value,
        )
        return workpaper_to_json(workpaper)
