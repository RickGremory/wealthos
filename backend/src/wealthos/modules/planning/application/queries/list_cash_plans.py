"""ListCashPlans query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.planning.domain.entities.cash_plan import CashPlan
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)


class ListCashPlansQuery:
    def __init__(self, cash_plans: CashPlanRepository) -> None:
        self._cash_plans = cash_plans

    def execute(
        self,
        organization_id: UUID,
        *,
        status: str | None = None,
        currency: str | None = None,
        include_archived: bool = False,
    ) -> list[CashPlan]:
        return self._cash_plans.list_by_organization(
            organization_id,
            status=status,
            currency=currency,
            include_archived=include_archived,
        )
