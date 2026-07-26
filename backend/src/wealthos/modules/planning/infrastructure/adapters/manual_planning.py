"""Manual planned cash flows owned by Planning itself."""

from __future__ import annotations

from datetime import UTC, datetime

from wealthos.modules.planning.domain.enums.cash_flow import CashFlowStatus
from wealthos.modules.planning.domain.enums.source import PlanningSource, SourceStatus
from wealthos.modules.planning.domain.ports.repositories import PlannedCashFlowRepository
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


class ManualPlanningAdapter:
    source_name = PlanningSource.MANUAL_PLANNING.value

    def __init__(self, planned_cash_flows: PlannedCashFlowRepository) -> None:
        self._planned = planned_cash_flows

    def collect(self, request: PlanningCollectionRequest) -> PlanningSourceContribution:
        now = datetime.now(UTC)
        currency = request.currency.strip().upper()
        flows: list[PlanningCashFlow] = []

        for item in self._planned.list_active_in_period(
            request.organization_id,
            currency=currency,
            period_start=request.period_start,
            period_end=request.period_end,
        ):
            amount = quantize_money(item.amount.amount)
            key = item.occurrence_key
            flows.append(
                PlanningCashFlow(
                    id=key,
                    organization_id=item.organization_id,
                    direction=item.direction,
                    amount=amount,
                    outstanding_amount=amount,
                    currency=currency,
                    expected_at=item.expected_at,
                    certainty=item.certainty,
                    status=CashFlowStatus.ACTIVE,
                    category="planned_cash_flow",
                    label=item.name,
                    source=PlanningSourceReference(
                        source_name=self.source_name,
                        resource_type="planned_cash_flow",
                        resource_id=str(item.id),
                        occurrence_key=key,
                        resource_version=item.version,
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
