"""GetCashFlow query."""

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
from wealthos.modules.dashboard.application.views.cash_flow import CashFlowSeriesView
from wealthos.modules.dashboard.domain.repositories.dashboard_read_repository import (
    DashboardReadRepository,
)
from wealthos.modules.dashboard.domain.value_objects.cash_flow_granularity import (
    CashFlowGranularity,
)


class GetCashFlowQuery:
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
        granularity: CashFlowGranularity | str,
    ) -> tuple[list[CashFlowSeriesView], DateRange, CashFlowGranularity]:
        gran = (
            granularity
            if isinstance(granularity, CashFlowGranularity)
            else CashFlowGranularity(granularity)
        )
        date_range = self._period_resolver.resolve(
            period=filters.period,
            timezone=timezone,
            date_from=filters.date_from,
            date_to=filters.date_to,
        )
        with timed(
            "dashboard.cash_flow",
            organization_id=str(organization_id),
            granularity=gran.value,
            period=filters.period.value,
        ):
            series = self._repository.get_cash_flow(
                organization_id,
                date_range,
                gran,
                primary_currency=primary_currency,
            )
        return series, date_range, gran
