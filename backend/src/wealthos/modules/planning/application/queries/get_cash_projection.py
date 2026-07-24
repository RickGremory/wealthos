"""GetCashProjection query."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from wealthos.modules.planning.application.services.cash_buffer_service import (
    CashBufferService,
)
from wealthos.modules.planning.application.services.cash_plan_occurrence_generator import (
    CashPlanOccurrenceGenerator,
)
from wealthos.modules.planning.application.services.cash_projection_service import (
    CashProjection,
    CashProjectionInput,
    CashProjectionItem,
    CashProjectionPoint,
    CashProjectionService,
)
from wealthos.modules.planning.application.services.safe_to_spend_service import (
    SafeToSpendResult,
    SafeToSpendService,
)
from wealthos.modules.planning.domain.exceptions import (
    CashPlanNotFoundError,
    InvalidCashScenario,
)
from wealthos.modules.planning.domain.repositories.cash_plan_item_match_repository import (
    CashPlanItemMatchRepository,
)
from wealthos.modules.planning.domain.repositories.cash_plan_item_repository import (
    CashPlanItemRepository,
)
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)
from wealthos.modules.planning.domain.repositories.planning_read_repository import (
    PlanningReadRepository,
)
from wealthos.modules.planning.domain.value_objects.cash_scenario import CashScenario
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionRepository,
)


@dataclass(frozen=True, slots=True)
class CashProjectionResult:
    projection: CashProjection
    scenario: str
    granularity: str
    opening_balance: Decimal
    points: tuple[CashProjectionPoint, ...]
    safe_to_spend: SafeToSpendResult | None
    currency: str


class GetCashProjectionQuery:
    def __init__(
        self,
        cash_plans: CashPlanRepository,
        items: CashPlanItemRepository,
        matches: CashPlanItemMatchRepository,
        read: PlanningReadRepository,
        projection: CashProjectionService | None = None,
        buffer: CashBufferService | None = None,
        safe_to_spend: SafeToSpendService | None = None,
        occurrences: CashPlanOccurrenceGenerator | None = None,
        transactions: TransactionRepository | None = None,
    ) -> None:
        self._cash_plans = cash_plans
        self._items = items
        self._matches = matches
        self._read = read
        self._projection = projection or CashProjectionService()
        self._buffer = buffer or CashBufferService()
        self._safe = safe_to_spend or SafeToSpendService()
        self._occurrences = occurrences or CashPlanOccurrenceGenerator()
        self._transactions = transactions

    def execute(
        self,
        organization_id: UUID,
        cash_plan_id: UUID,
        *,
        scenario: str = "expected",
        granularity: str = "day",
        as_of: date | None = None,
    ) -> CashProjectionResult:
        plan = self._cash_plans.get_by_id(organization_id, cash_plan_id)
        if plan is None:
            raise CashPlanNotFoundError("Cash plan not found.")
        try:
            scenario_vo = CashScenario(scenario)
        except Exception as exc:
            raise InvalidCashScenario(str(exc)) from exc

        account_ids = self._cash_plans.list_account_ids(organization_id, cash_plan_id)
        opening = self._resolve_opening(organization_id, plan, account_ids)

        items = self._items.list_by_plan(organization_id, cash_plan_id, include_cancelled=True)
        plan_matches = self._matches.list_by_plan(organization_id, cash_plan_id)
        matches_by_item: dict[UUID, list] = {}
        for match in plan_matches:
            matches_by_item.setdefault(match.cash_plan_item_id, []).append(match)

        projection_items: list[CashProjectionItem] = []
        for item in items:
            item_matches = matches_by_item.get(item.id, [])
            matched_amount = sum((m.matched_amount.amount for m in item_matches), Decimal("0.00"))
            matched_dates = tuple(
                self._match_date(organization_id, match, fallback=item.expected_date)
                for match in item_matches
            )
            occurrence_dates = self._occurrences.expand(
                expected_date=item.expected_date,
                recurrence_rule=item.recurrence_rule,
                date_from=plan.date_from,
                date_to=plan.date_to,
            )
            if not occurrence_dates and item.recurrence_rule:
                continue
            dates = occurrence_dates or (item.expected_date,)
            # Matches apply to the series once; remaining planned amount stays on later dates.
            remaining_match = matched_amount
            for index, occurrence_date in enumerate(dates):
                applied = remaining_match if index == 0 else Decimal("0.00")
                if index == 0:
                    remaining_match = Decimal("0.00")
                projection_items.append(
                    CashProjectionItem(
                        item_id=item.id,
                        item_type=item.item_type.value,
                        expected_date=occurrence_date,
                        amount=item.amount.amount,
                        probability=item.probability.value,
                        status=item.status.value,
                        matched_amount=applied,
                        matched_dates=matched_dates if index == 0 else (),
                    )
                )

        projection = self._projection.project(
            CashProjectionInput(
                opening_balance=opening,
                date_from=plan.date_from,
                date_to=plan.date_to,
                items=tuple(projection_items),
                scenario=scenario_vo.value,
            )
        )
        points = _aggregate_points(projection.points, granularity)

        avg_daily = self._read.get_average_daily_expenses(
            organization_id, plan.currency, lookback_days=90
        )
        buffer = self._buffer.compute(
            buffer_type=plan.minimum_cash_buffer_type.value,
            buffer_value=plan.minimum_cash_buffer_value,
            avg_daily_expense=avg_daily,
        )
        committed = sum(
            (
                item.amount.amount
                for item in items
                if item.item_type.is_outflow
                and item.status.value in {"confirmed", "planned", "partially_matched", "overdue"}
                and not item.status.is_cancelled
            ),
            Decimal("0.00"),
        )
        liquid = opening
        safe = self._safe.calculate(
            liquid_balance=liquid,
            committed_outflows=committed,
            tax_reserve_shortfall=Decimal("0.00"),
            minimum_cash_buffer=buffer,
        )

        return CashProjectionResult(
            projection=projection,
            scenario=scenario_vo.value,
            granularity=granularity,
            opening_balance=opening,
            points=points,
            safe_to_spend=safe,
            currency=plan.currency.value,
        )

    def _match_date(self, organization_id: UUID, match, *, fallback: date) -> date:
        if self._transactions is None:
            return fallback
        tx = self._transactions.get_by_id(organization_id, match.transaction_id)
        if tx is None:
            return fallback
        return tx.occurred_at.date()

    def _resolve_opening(self, organization_id: UUID, plan, account_ids: list[UUID]) -> Decimal:
        if plan.opening_balance_mode.is_manual and plan.manual_opening_balance is not None:
            return plan.manual_opening_balance.amount

        ids = account_ids if plan.opening_balance_mode.is_selected_accounts else None
        balances = self._read.get_liquid_account_balances(
            organization_id,
            plan.currency,
            account_ids=ids,
        )
        return sum((row.current_balance for row in balances), Decimal("0.00"))


def _aggregate_points(
    points: tuple[CashProjectionPoint, ...],
    granularity: str,
) -> tuple[CashProjectionPoint, ...]:
    g = (granularity or "day").strip().lower()
    if g == "day" or not points:
        return points

    buckets: dict[date, list[CashProjectionPoint]] = {}
    for point in points:
        if g == "week":
            key = point.date - timedelta(days=point.date.weekday())
        elif g == "month":
            key = date(point.date.year, point.date.month, 1)
        else:
            return points
        buckets.setdefault(key, []).append(point)

    aggregated: list[CashProjectionPoint] = []
    for key in sorted(buckets):
        group = buckets[key]
        inflows = sum((p.inflows for p in group), Decimal("0.00"))
        outflows = sum((p.outflows for p in group), Decimal("0.00"))
        ending = group[-1].ending_balance
        lowest = min(p.lowest_intraday_balance for p in group)
        aggregated.append(
            CashProjectionPoint(
                date=key,
                inflows=inflows,
                outflows=outflows,
                ending_balance=ending,
                lowest_intraday_balance=lowest,
            )
        )
    return tuple(aggregated)
