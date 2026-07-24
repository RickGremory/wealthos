"""GetAccountSummary query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.dashboard.application.views.account_balance import (
    AccountBalanceGroupView,
)
from wealthos.modules.dashboard.domain.repositories.dashboard_read_repository import (
    DashboardReadRepository,
)


class GetAccountSummaryQuery:
    def __init__(self, repository: DashboardReadRepository) -> None:
        self._repository = repository

    def execute(
        self,
        organization_id: UUID,
        *,
        primary_currency: str,
        include_archived: bool = False,
    ) -> list[AccountBalanceGroupView]:
        return self._repository.get_account_balances(
            organization_id,
            include_archived=include_archived,
            primary_currency=primary_currency,
        )
