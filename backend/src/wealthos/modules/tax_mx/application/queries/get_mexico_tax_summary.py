"""GetMexicoTaxSummary query."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.tax_mx.application.queries.get_mexico_tax_workpaper import (
    GetMexicoTaxWorkpaperQuery,
)
from wealthos.modules.tax_mx.application.services.tax_period_staleness_service import (
    TaxPeriodStalenessService,
)
from wealthos.modules.tax_mx.domain.exceptions import MexicoTaxPeriodNotFound
from wealthos.modules.taxes.application.services.tax_period_generator import TaxPeriodGenerator
from wealthos.modules.taxes.domain.repositories.tax_period_repository import TaxPeriodRepository
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import TaxProfileRepository


@dataclass(frozen=True, slots=True)
class MexicoTaxSummaryView:
    tax_profile_id: UUID
    period_id: UUID | None
    currency: str
    income_tax_due: Decimal
    vat_due: Decimal
    estimated_total_due: Decimal
    income_tax_reserve_recommended: Decimal
    vat_reserve_recommended: Decimal
    is_stale: bool
    calculated_at: object | None
    latest_relevant_change_at: object | None


class GetMexicoTaxSummaryQuery:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        periods: TaxPeriodRepository,
        workpaper: GetMexicoTaxWorkpaperQuery,
        staleness: TaxPeriodStalenessService,
        period_generator: TaxPeriodGenerator,
    ) -> None:
        self._profiles = profiles
        self._periods = periods
        self._workpaper = workpaper
        self._staleness = staleness
        self._period_generator = period_generator

    def execute(
        self, organization_id: UUID, *, period_id: UUID | None = None
    ) -> MexicoTaxSummaryView:
        profile = self._profiles.get_active(organization_id)
        if profile is None:
            raise MexicoTaxPeriodNotFound("Active tax profile not found.")

        self._period_generator.ensure_current_period(profile)
        if period_id is None:
            rows = self._periods.list_by_profile(organization_id, profile.id)
            period = rows[0] if rows else None
        else:
            period = self._periods.get_by_id(organization_id, period_id)
        if period is None:
            raise MexicoTaxPeriodNotFound("Tax period not found.")

        paper = self._workpaper.execute(organization_id, period.id, recompute=False)
        stale = self._staleness.evaluate(period, organization_id)
        isr_due = Decimal(str(paper.get("income_tax_due", "0")))
        vat_due = Decimal(str(paper.get("vat_due", "0")))
        total = Decimal(str(paper.get("estimated_total_due", "0")))
        return MexicoTaxSummaryView(
            tax_profile_id=profile.id,
            period_id=period.id,
            currency=str(paper.get("currency", profile.currency.value)),
            income_tax_due=isr_due,
            vat_due=vat_due,
            estimated_total_due=total,
            income_tax_reserve_recommended=isr_due,
            vat_reserve_recommended=vat_due,
            is_stale=stale.is_stale,
            calculated_at=stale.calculated_at,
            latest_relevant_change_at=stale.latest_relevant_change_at,
        )
