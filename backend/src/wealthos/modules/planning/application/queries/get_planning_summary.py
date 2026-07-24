"""GetPlanningSummary query."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.planning.application.queries.get_cash_projection import (
    GetCashProjectionQuery,
)
from wealthos.modules.planning.domain.repositories.budget_repository import BudgetRepository
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)


@dataclass(frozen=True, slots=True)
class PlanningSummary:
    active_budgets: int
    draft_budgets: int
    active_cash_plans: int
    draft_cash_plans: int
    currency: str | None
    safe_to_spend: Decimal | None
    funding_gap: Decimal | None
    primary_cash_plan_id: UUID | None


class GetPlanningSummaryQuery:
    def __init__(
        self,
        budgets: BudgetRepository,
        cash_plans: CashPlanRepository,
        projection_query: GetCashProjectionQuery | None = None,
    ) -> None:
        self._budgets = budgets
        self._cash_plans = cash_plans
        self._projection_query = projection_query

    def execute(self, organization_id: UUID) -> PlanningSummary:
        budgets = self._budgets.list_by_organization(organization_id, include_archived=False)
        cash_plans = self._cash_plans.list_by_organization(organization_id, include_archived=False)

        active_budgets = sum(1 for b in budgets if b.status.is_active)
        draft_budgets = sum(1 for b in budgets if b.status.is_draft)
        active_plans = [p for p in cash_plans if p.status.is_active]
        draft_plans = sum(1 for p in cash_plans if p.status.is_draft)

        primary = active_plans[0] if active_plans else None
        safe = None
        gap = None
        currency = primary.currency.value if primary else None
        if primary is not None and self._projection_query is not None:
            result = self._projection_query.execute(organization_id, primary.id)
            if result.safe_to_spend is not None:
                safe = result.safe_to_spend.safe_to_spend
                gap = result.safe_to_spend.funding_gap

        return PlanningSummary(
            active_budgets=active_budgets,
            draft_budgets=draft_budgets,
            active_cash_plans=len(active_plans),
            draft_cash_plans=draft_plans,
            currency=currency,
            safe_to_spend=safe,
            funding_gap=gap,
            primary_cash_plan_id=primary.id if primary else None,
        )
