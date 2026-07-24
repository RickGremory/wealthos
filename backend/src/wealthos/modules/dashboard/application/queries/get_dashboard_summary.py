"""GetDashboardSummary query."""

from __future__ import annotations

from uuid import UUID

from wealthos.core.timing import timed
from wealthos.modules.dashboard.application.queries.period_filters import (
    DashboardPeriodFilters,
)
from wealthos.modules.dashboard.application.services.dashboard_period_resolver import (
    DashboardPeriodResolver,
)
from wealthos.modules.dashboard.application.value_objects.date_range import DateRange
from wealthos.modules.dashboard.application.views.summary import DashboardSummaryView
from wealthos.modules.dashboard.domain.repositories.dashboard_read_repository import (
    DashboardReadRepository,
)


class GetDashboardSummaryQuery:
    def __init__(
        self,
        repository: DashboardReadRepository,
        period_resolver: DashboardPeriodResolver,
    ) -> None:
        self._repository = repository
        self._period_resolver = period_resolver

    def execute(
        self,
        organization_id: UUID,
        *,
        timezone: str,
        primary_currency: str,
        filters: DashboardPeriodFilters,
    ) -> tuple[DashboardSummaryView, DateRange]:
        date_range = self._period_resolver.resolve(
            period=filters.period,
            timezone=timezone,
            date_from=filters.date_from,
            date_to=filters.date_to,
        )
        with timed(
            "dashboard.summary",
            organization_id=str(organization_id),
            period=filters.period.value,
        ):
            summary = self._repository.get_summary(
                organization_id,
                date_range,
                primary_currency=primary_currency,
            )
        return summary, date_range
