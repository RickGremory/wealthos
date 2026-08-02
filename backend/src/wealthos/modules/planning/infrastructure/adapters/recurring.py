"""Map Recurring open occurrences → Planning cash flows (SPEC-005 PR6)."""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from wealthos.modules.planning.domain.enums.cash_flow import (
    CashFlowCertainty,
    CashFlowDirection,
    CashFlowStatus,
)
from wealthos.modules.planning.domain.enums.source import PlanningSource, SourceStatus
from wealthos.modules.planning.domain.ports.source_adapter import (
    PlanningCollectionRequest,
    PlanningSourceContribution,
)
from wealthos.modules.planning.domain.value_objects.cash_flow import PlanningCashFlow
from wealthos.modules.planning.domain.value_objects.collection_warning import (
    PlanningSourceMetadata,
)
from wealthos.modules.planning.domain.value_objects.money_utils import quantize_money
from wealthos.modules.planning.domain.value_objects.source_reference import (
    PlanningSourceReference,
)
from wealthos.modules.recurring.application.services.occurrence_projector import (
    RecurringOccurrenceProjector,
)
from wealthos.modules.recurring.domain.enums.occurrence import RecurringOccurrenceStatus
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringCertainty,
    RecurringDirection,
)
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringAggregateRepository,
    RecurringSettlementRepository,
)


class RecurringPlanningAdapter:
    """Replace stub: project manual Recurring occurrences into Planning."""

    source_name = PlanningSource.RECURRING.value

    def __init__(
        self,
        repo: RecurringAggregateRepository,
        settlements: RecurringSettlementRepository | None = None,
        projector: RecurringOccurrenceProjector | None = None,
    ) -> None:
        self._projector = projector or RecurringOccurrenceProjector(repo, settlements)

    def collect(self, request: PlanningCollectionRequest) -> PlanningSourceContribution:
        from wealthos.core.timing import timed

        with timed(
            "recurring.planning_adapter",
            organization_id=str(request.organization_id),
            currency=request.currency.strip().upper(),
        ):
            return self._collect(request)

    def _collect(self, request: PlanningCollectionRequest) -> PlanningSourceContribution:
        now = datetime.now(UTC)
        currency = request.currency.strip().upper()
        try:
            zone = ZoneInfo(request.timezone)
        except Exception:
            zone = ZoneInfo("UTC")

        local_start = request.period_start.astimezone(zone).date()
        local_end = request.period_end.astimezone(zone).date()
        evaluated_on = request.calculated_at.astimezone(zone).date()

        projected = self._projector.project(
            organization_id=request.organization_id,
            period_start=local_start,
            period_end=local_end,
            evaluated_on=evaluated_on,
            timezone=request.timezone,
            currency=currency,
            include_externally_managed=False,
            include_transfers=False,
        )

        flows: list[PlanningCashFlow] = []
        for item in projected:
            direction = _map_direction(item.direction)
            if direction is None:
                continue
            amount = quantize_money(item.outstanding_amount)
            status = (
                CashFlowStatus.PARTIALLY_SETTLED
                if item.status is RecurringOccurrenceStatus.PARTIALLY_SETTLED
                else CashFlowStatus.ACTIVE
            )
            flows.append(
                PlanningCashFlow(
                    id=item.occurrence_key,
                    organization_id=request.organization_id,
                    direction=direction,
                    amount=quantize_money(item.occurrence.expected_amount),
                    outstanding_amount=amount,
                    currency=currency,
                    expected_at=item.occurrence.expected_at,
                    certainty=_map_certainty(item.occurrence.certainty),
                    status=status,
                    category="recurring",
                    label=item.name,
                    source=PlanningSourceReference(
                        source_name=self.source_name,
                        resource_type="recurring_rule",
                        resource_id=str(item.occurrence.recurring_rule_id),
                        occurrence_key=item.occurrence_key,
                        resource_version=item.rule_version,
                    ),
                )
            )

        return PlanningSourceContribution(
            source_name=self.source_name,
            cash_flows=tuple(flows),
            metadata=PlanningSourceMetadata(
                source_name=self.source_name,
                collected_at=now,
                data_as_of=now,
                status=SourceStatus.AVAILABLE,
            ),
        )


def _map_direction(direction: RecurringDirection) -> CashFlowDirection | None:
    if direction is RecurringDirection.INFLOW:
        return CashFlowDirection.INFLOW
    if direction is RecurringDirection.OUTFLOW:
        return CashFlowDirection.OUTFLOW
    return None


def _map_certainty(certainty: RecurringCertainty) -> CashFlowCertainty:
    if certainty is RecurringCertainty.CONFIRMED:
        return CashFlowCertainty.CONFIRMED
    if certainty is RecurringCertainty.ESTIMATED:
        return CashFlowCertainty.ESTIMATED
    return CashFlowCertainty.EXPECTED
