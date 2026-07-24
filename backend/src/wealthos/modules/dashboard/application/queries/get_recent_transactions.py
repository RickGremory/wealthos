"""GetRecentTransactions query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.dashboard.application.views.recent_transaction import (
    RecentTransactionView,
)
from wealthos.modules.dashboard.domain.repositories.dashboard_read_repository import (
    DashboardReadRepository,
)


class GetRecentTransactionsQuery:
    def __init__(self, repository: DashboardReadRepository) -> None:
        self._repository = repository

    def execute(
        self,
        organization_id: UUID,
        *,
        limit: int,
    ) -> list[RecentTransactionView]:
        return self._repository.get_recent_transactions(
            organization_id,
            limit=limit,
        )
