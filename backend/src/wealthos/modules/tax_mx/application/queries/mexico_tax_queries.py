"""Queries for Mexico tax module."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from uuid import UUID

from wealthos.modules.tax_mx.application.services.mexico_tax_calculation_service import (
    MexicoTaxTransactionView,
)
from wealthos.modules.tax_mx.domain.entities.mexico_tax_configuration import (
    MexicoTaxConfiguration,
)
from wealthos.modules.tax_mx.domain.exceptions import (
    MexicoTaxConfigurationNotFound,
    MexicoTaxPeriodNotFound,
    MexicoTaxProfileRequired,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_catalog_repository import (
    MexicoTaxCatalogRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_category_mapping_repository import (
    MexicoTaxCategoryMappingRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_configuration_repository import (
    MexicoTaxConfigurationRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_read_repository import (
    MexicoTaxReadRepository,
)
from wealthos.modules.tax_mx.domain.repositories.mexico_tax_snapshot_repository import (
    MexicoTaxSnapshotRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_calculation_repository import (
    TaxCalculationRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_payment_repository import (
    TaxPaymentRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_period_repository import (
    TaxPeriodRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_read_repository import TaxReadRepository

_ZERO = Decimal("0.00")
_CATALOG_PATH = Path(__file__).resolve().parents[2] / "catalogs" / "data" / "catalogs-v1.json"


class GetMexicoTaxConfigurationQuery:
    def __init__(
        self,
        configurations: MexicoTaxConfigurationRepository,
        profiles: TaxProfileRepository,
    ) -> None:
        self._configurations = configurations
        self._profiles = profiles

    def execute(
        self, organization_id: UUID, tax_profile_id: UUID | None = None
    ) -> MexicoTaxConfiguration:
        profile = (
            self._profiles.get_by_id(organization_id, tax_profile_id)
            if tax_profile_id is not None
            else self._profiles.get_active(organization_id)
        )
        if profile is None:
            raise MexicoTaxProfileRequired("Tax profile not found.")
        configuration = self._configurations.get_current(profile.id)
        if configuration is None:
            raise MexicoTaxConfigurationNotFound("No current Mexico tax configuration.")
        return configuration


class ListMexicoTaxCatalogsQuery:
    def __init__(self, catalogs: MexicoTaxCatalogRepository) -> None:
        self._catalogs = catalogs

    def execute(self) -> dict:
        if self._catalogs.is_empty():
            from wealthos.modules.tax_mx.catalogs.import_catalog import import_catalog

            import_catalog()
        return {
            "catalog_version": "v1",
            "catalogs": {
                "tax_regimes": self._catalogs.list_catalog("tax_regimes"),
                "vat_rates": self._catalogs.list_catalog("vat_rates"),
                "withholding_types": self._catalogs.list_catalog("withholding_types"),
            },
        }


class ListMexicoCategoryMappingsQuery:
    def __init__(self, mappings: MexicoTaxCategoryMappingRepository) -> None:
        self._mappings = mappings

    def execute(self, organization_id: UUID, tax_profile_id: UUID):
        return self._mappings.list_by_profile(organization_id, tax_profile_id)


class ListUnclassifiedTaxTransactionsQuery:
    def __init__(self, read: MexicoTaxReadRepository) -> None:
        self._read = read

    def execute(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        **filters,
    ) -> tuple[list[MexicoTaxTransactionView], int]:
        return self._read.get_unclassified_transactions(organization_id, tax_profile_id, **filters)


class GetMexicoTaxWorkpaperQuery:
    def __init__(
        self,
        periods: TaxPeriodRepository,
        calculations: TaxCalculationRepository,
        snapshots: MexicoTaxSnapshotRepository,
        read: MexicoTaxReadRepository,
    ) -> None:
        self._periods = periods
        self._calculations = calculations
        self._snapshots = snapshots
        self._read = read

    def execute(self, organization_id: UUID, period_id: UUID) -> dict:
        period = self._periods.get_by_id(organization_id, period_id)
        if period is None:
            raise MexicoTaxPeriodNotFound("Tax period not found.")
        latest = self._calculations.get_latest_by_period(organization_id, period_id)
        if latest is None:
            raise MexicoTaxPeriodNotFound("No calculation snapshot for this period.")
        snapshot = self._snapshots.get_by_calculation(organization_id, latest.id)
        if snapshot is None:
            raise MexicoTaxPeriodNotFound("Mexico workpaper snapshot not found.")
        wj = snapshot
        changed = self._read.latest_relevant_change_at(
            organization_id,
            date_from=period.date_from,
            date_to=period.date_to,
        )
        is_stale = bool(
            period.calculated_at is not None
            and changed is not None
            and changed > period.calculated_at
        )
        return {
            "period_id": wj.get("period_id", str(period.id)),
            "currency": wj["currency"],
            "income": wj.get("income")
            or {
                "collected": wj.get("collected_income", "0"),
                "taxable": wj.get("taxable_income", "0"),
                "exempt": wj.get("exempt_income", "0"),
            },
            "expenses": wj.get("expenses")
            or {
                "paid": wj.get("paid_expenses", "0"),
                "deductible": wj.get("deductible_expenses", "0"),
                "non_deductible": wj.get("non_deductible_expenses", "0"),
            },
            "vat": wj.get("vat")
            or {
                "output": wj.get("output_vat", "0"),
                "identified_input": wj.get("identified_input_vat", "0"),
                "creditable": wj.get("creditable_vat", "0"),
                "withheld": wj.get("withheld_vat", "0"),
                "due": wj.get("vat_due", "0"),
                "credit_balance": wj.get("vat_credit_balance", "0"),
            },
            "income_tax": wj.get("income_tax")
            or {
                "estimated_before_withholdings": wj.get("estimated_income_tax", "0"),
                "withheld": wj.get("withheld_income_tax", "0"),
                "due": wj.get("income_tax_due", "0"),
            },
            "estimated_total_due": wj.get("estimated_total_due", "0"),
            "quality": wj.get("quality", {}),
            "warnings": wj.get("warnings", []),
            "is_stale": is_stale,
            "version": latest.version,
        }


class GetMexicoTaxSummaryQuery:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        configurations: MexicoTaxConfigurationRepository,
        periods: TaxPeriodRepository,
        calculations: TaxCalculationRepository,
        snapshots: MexicoTaxSnapshotRepository,
        payments: TaxPaymentRepository,
        tax_read: TaxReadRepository,
    ) -> None:
        self._profiles = profiles
        self._configurations = configurations
        self._periods = periods
        self._calculations = calculations
        self._snapshots = snapshots
        self._payments = payments
        self._tax_read = tax_read

    def execute(self, organization_id: UUID) -> dict:
        profile = self._profiles.get_active(organization_id)
        if profile is None:
            return {
                "currency": "MXN",
                "income_tax": {
                    "estimated_due": "0.00",
                    "paid": "0.00",
                    "recommended_reserve": "0.00",
                },
                "vat": {
                    "estimated_due": "0.00",
                    "paid": "0.00",
                    "recommended_reserve": "0.00",
                },
                "total": {
                    "estimated_due": "0.00",
                    "reserved": "0.00",
                    "shortfall": "0.00",
                },
            }
        periods = self._periods.list_by_profile(organization_id, profile.id)
        isr_due = _ZERO
        vat_due = _ZERO
        paid = _ZERO
        if periods:
            current = periods[0]
            latest = self._calculations.get_latest_by_period(organization_id, current.id)
            if latest is not None:
                snap = self._snapshots.get_by_calculation(organization_id, latest.id)
                if snap is not None:
                    wj = snap
                    income_tax = wj.get("income_tax") or {}
                    vat = wj.get("vat") or {}
                    isr_due = Decimal(str(income_tax.get("due", wj.get("income_tax_due", "0"))))
                    vat_due = Decimal(str(vat.get("due", wj.get("vat_due", "0"))))
                paid = self._payments.sum_by_period(
                    organization_id, current.id, currency=profile.currency.value
                )
        reserved = _ZERO
        if profile.reserve_account_id is not None:
            balance = self._tax_read.get_reserve_account_balance(
                organization_id, profile.reserve_account_id
            )
            reserved = balance if balance is not None else _ZERO
        total_due = isr_due + vat_due
        return {
            "currency": profile.currency.value,
            "income_tax": {
                "estimated_due": str(isr_due),
                "paid": "0.00",
                "recommended_reserve": str(max(isr_due, _ZERO)),
            },
            "vat": {
                "estimated_due": str(vat_due),
                "paid": "0.00",
                "recommended_reserve": str(max(vat_due, _ZERO)),
            },
            "total": {
                "estimated_due": str(total_due),
                "reserved": str(reserved),
                "shortfall": str(max(total_due - paid - reserved, _ZERO)),
            },
        }
