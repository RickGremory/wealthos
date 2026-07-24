"""Generate fiscal periods idempotently from a tax profile."""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date

from wealthos.modules.taxes.domain.entities.tax_period import TaxPeriod
from wealthos.modules.taxes.domain.entities.tax_profile import TaxProfile
from wealthos.modules.taxes.domain.repositories.tax_period_repository import (
    TaxPeriodRepository,
)


@dataclass(frozen=True, slots=True)
class PeriodWindow:
    date_from: date
    date_to: date
    period_type: str


class TaxPeriodGenerator:
    def __init__(self, periods: TaxPeriodRepository) -> None:
        self._periods = periods

    def ensure_current_period(
        self,
        profile: TaxProfile,
        *,
        today: date | None = None,
    ) -> TaxPeriod:
        today = today or date.today()
        window = self.window_for(profile, today)
        existing = self._periods.get_by_range(
            profile.id,
            window.date_from,
            window.date_to,
        )
        if existing is not None:
            return existing
        period = TaxPeriod.create(
            organization_id=profile.organization_id,
            tax_profile_id=profile.id,
            period_type=window.period_type,
            date_from=window.date_from,
            date_to=window.date_to,
            currency=profile.currency.value,
        )
        return self._periods.add(period)

    def window_for(self, profile: TaxProfile, on_date: date) -> PeriodWindow:
        freq = profile.filing_frequency.value
        if freq == "monthly":
            start = date(on_date.year, on_date.month, 1)
            end = date(on_date.year, on_date.month, monthrange(on_date.year, on_date.month)[1])
            return PeriodWindow(start, end, "monthly")
        if freq == "quarterly":
            # Quarters relative to fiscal_year_start_month.
            offset = (on_date.month - profile.fiscal_year_start_month) % 12
            quarter_index = offset // 3
            start_month = ((profile.fiscal_year_start_month - 1 + quarter_index * 3) % 12) + 1
            start_year = on_date.year
            if start_month > on_date.month:
                start_year -= 1
            start = date(start_year, start_month, 1)
            end_month = ((start_month - 1 + 2) % 12) + 1
            end_year = start_year if end_month >= start_month else start_year + 1
            end = date(end_year, end_month, monthrange(end_year, end_month)[1])
            return PeriodWindow(start, end, "quarterly")
        # annual
        start_month = profile.fiscal_year_start_month
        start_year = on_date.year if on_date.month >= start_month else on_date.year - 1
        start = date(start_year, start_month, 1)
        end_year = start_year + 1
        end_month = start_month
        # day before next fiscal year start
        if end_month == 1:
            end = date(end_year, 1, 1)
            from datetime import timedelta

            end = end - timedelta(days=1)
        else:
            end = date(end_year, end_month, 1)
            from datetime import timedelta

            end = end - timedelta(days=1)
        return PeriodWindow(start, end, "annual")
