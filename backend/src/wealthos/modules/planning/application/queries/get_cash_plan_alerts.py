"""GetCashPlanAlerts query."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from wealthos.modules.planning.application.queries.get_cash_projection import (
    GetCashProjectionQuery,
)
from wealthos.modules.planning.application.services.cash_alert_service import (
    CashAlert,
    CashAlertService,
    OverdueInflow,
)
from wealthos.modules.planning.application.services.cash_buffer_service import (
    CashBufferService,
)
from wealthos.modules.planning.domain.exceptions import CashPlanNotFoundError
from wealthos.modules.planning.domain.repositories.cash_plan_item_repository import (
    CashPlanItemRepository,
)
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)
from wealthos.modules.planning.domain.repositories.planning_read_repository import (
    PlanningReadRepository,
)


class GetCashPlanAlertsQuery:
    def __init__(
        self,
        cash_plans: CashPlanRepository,
        items: CashPlanItemRepository,
        read: PlanningReadRepository,
        projection_query: GetCashProjectionQuery,
        alerts: CashAlertService | None = None,
        buffer: CashBufferService | None = None,
    ) -> None:
        self._cash_plans = cash_plans
        self._items = items
        self._read = read
        self._projection_query = projection_query
        self._alerts = alerts or CashAlertService()
        self._buffer = buffer or CashBufferService()

    def execute(
        self,
        organization_id: UUID,
        cash_plan_id: UUID,
        *,
        scenario: str = "expected",
        as_of: date | None = None,
    ) -> tuple[CashAlert, ...]:
        plan = self._cash_plans.get_by_id(organization_id, cash_plan_id)
        if plan is None:
            raise CashPlanNotFoundError("Cash plan not found.")

        projection_result = self._projection_query.execute(
            organization_id,
            cash_plan_id,
            scenario=scenario,
            as_of=as_of,
        )
        today = as_of or date.today()
        items = self._items.list_by_plan(organization_id, cash_plan_id)
        overdue = [
            OverdueInflow(
                expected_date=item.expected_date,
                amount=item.amount.amount,
                description=item.description,
            )
            for item in items
            if item.item_type.is_inflow
            and item.expected_date < today
            and item.status.value not in {"matched", "cancelled"}
        ]

        avg_daily = self._read.get_average_daily_expenses(
            organization_id, plan.currency, lookback_days=90
        )
        buffer = self._buffer.compute(
            buffer_type=plan.minimum_cash_buffer_type.value,
            buffer_value=plan.minimum_cash_buffer_value,
            avg_daily_expense=avg_daily,
        )
        return self._alerts.generate(
            projection=projection_result.projection,
            minimum_cash_buffer=buffer,
            overdue_inflows=overdue,
            as_of=today,
        )
