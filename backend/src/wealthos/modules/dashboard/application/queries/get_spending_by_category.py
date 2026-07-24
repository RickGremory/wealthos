"""GetSpendingByCategory query."""

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
from wealthos.modules.dashboard.application.views.category_spending import (
    CategorySpendingSeriesView,
)
from wealthos.modules.dashboard.domain.repositories.dashboard_read_repository import (
    DashboardReadRepository,
)
from wealthos.modules.dashboard.domain.value_objects.category_grouping import (
    CategoryGrouping,
)


class GetSpendingByCategoryQuery:
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
        limit: int,
        group_by: CategoryGrouping | str = "root",
    ) -> tuple[list[CategorySpendingSeriesView], DateRange]:
        grouping = (
            group_by if isinstance(group_by, CategoryGrouping) else CategoryGrouping(group_by)
        )
        date_range = self._period_resolver.resolve(
            period=filters.period,
            timezone=timezone,
            date_from=filters.date_from,
            date_to=filters.date_to,
        )
        with timed(
            "dashboard.spending_by_category",
            organization_id=str(organization_id),
            group_by=grouping.value,
            period=filters.period.value,
        ):
            series = self._repository.get_spending_by_category(
                organization_id,
                date_range,
                limit=limit,
                group_by=grouping,
                primary_currency=primary_currency,
            )
        return series, date_range
