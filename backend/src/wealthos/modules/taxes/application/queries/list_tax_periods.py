"""ListTaxPeriods query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.taxes.application.services.tax_period_generator import (
    TaxPeriodGenerator,
)
from wealthos.modules.taxes.domain.entities.tax_period import TaxPeriod
from wealthos.modules.taxes.domain.exceptions import TaxProfileNotFound
from wealthos.modules.taxes.domain.repositories.tax_period_repository import (
    TaxPeriodRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)


class ListTaxPeriodsQuery:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        periods: TaxPeriodRepository,
        period_generator: TaxPeriodGenerator | None = None,
    ) -> None:
        self._profiles = profiles
        self._periods = periods
        self._period_generator = period_generator or TaxPeriodGenerator(periods)

    def execute(self, organization_id: UUID, tax_profile_id: UUID) -> list[TaxPeriod]:
        profile = self._profiles.get_by_id(organization_id, tax_profile_id)
        if profile is None:
            raise TaxProfileNotFound("Tax profile not found.")
        if profile.is_active:
            self._period_generator.ensure_current_period(profile)
        return self._periods.list_by_profile(organization_id, tax_profile_id)
