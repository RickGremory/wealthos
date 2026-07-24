"""Dashboard read repository port."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.dashboard.application.value_objects.date_range import DateRange
from wealthos.modules.dashboard.application.views.account_balance import (
    AccountBalanceGroupView,
)
from wealthos.modules.dashboard.application.views.cash_flow import CashFlowSeriesView
from wealthos.modules.dashboard.application.views.category_spending import (
    CategorySpendingSeriesView,
)
from wealthos.modules.dashboard.application.views.recent_transaction import (
    RecentTransactionView,
)
from wealthos.modules.dashboard.application.views.summary import DashboardSummaryView
from wealthos.modules.dashboard.domain.value_objects.cash_flow_granularity import (
    CashFlowGranularity,
)
from wealthos.modules.dashboard.domain.value_objects.category_grouping import (
    CategoryGrouping,
)


class DashboardReadRepository(Protocol):
    def get_summary(
        self,
        organization_id: UUID,
        period: DateRange,
        *,
        primary_currency: str,
    ) -> DashboardSummaryView: ...

    def get_cash_flow(
        self,
        organization_id: UUID,
        period: DateRange,
        granularity: CashFlowGranularity,
        *,
        primary_currency: str,
    ) -> list[CashFlowSeriesView]: ...

    def get_spending_by_category(
        self,
        organization_id: UUID,
        period: DateRange,
        *,
        limit: int,
        group_by: CategoryGrouping,
        primary_currency: str,
    ) -> list[CategorySpendingSeriesView]: ...

    def get_account_balances(
        self,
        organization_id: UUID,
        *,
        include_archived: bool = False,
        primary_currency: str,
    ) -> list[AccountBalanceGroupView]: ...

    def get_recent_transactions(
        self,
        organization_id: UUID,
        *,
        limit: int,
    ) -> list[RecentTransactionView]: ...
