"""One occurrence_key → at most one effect on the projection (§30, §14)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import timedelta

from wealthos.modules.planning.domain.enums.alert import (
    AlertSeverity,
    PlanningAlertCode,
    PlanningExclusionReason,
)
from wealthos.modules.planning.domain.enums.source import source_precedence
from wealthos.modules.planning.domain.value_objects.alerts import (
    ExcludedPlanningItem,
    PlanningAlert,
)
from wealthos.modules.planning.domain.value_objects.cash_flow import PlanningCashFlow

#: Heuristic duplicates within this window only raise a warning — never a drop.
HEURISTIC_DATE_WINDOW = timedelta(days=3)


@dataclass(frozen=True, slots=True)
class DeduplicationResult:
    cash_flows: tuple[PlanningCashFlow, ...]
    excluded: tuple[ExcludedPlanningItem, ...]
    alerts: tuple[PlanningAlert, ...]


class PlanningCashFlowDeduplicator:
    """Exact key wins by source precedence; look-alikes only get flagged."""

    def deduplicate(self, cash_flows: Iterable[PlanningCashFlow]) -> DeduplicationResult:
        winners: dict[str, PlanningCashFlow] = {}
        order: list[str] = []
        excluded: list[ExcludedPlanningItem] = []
        alerts: list[PlanningAlert] = []

        for flow in cash_flows:
            key = flow.occurrence_key
            incumbent = winners.get(key)
            if incumbent is None:
                winners[key] = flow
                order.append(key)
                continue

            challenger_wins = source_precedence(flow.source_name) > source_precedence(
                incumbent.source_name
            )
            loser = incumbent if challenger_wins else flow
            if challenger_wins:
                winners[key] = flow

            excluded.append(
                ExcludedPlanningItem(
                    occurrence_key=key,
                    label=loser.label,
                    reason_code=PlanningExclusionReason.DUPLICATE_OCCURRENCE.value,
                    amount=loser.outstanding_amount,
                    currency=loser.currency,
                    date=loser.expected_at,
                    source_name=loser.source_name,
                )
            )
            alerts.append(
                PlanningAlert(
                    code=PlanningAlertCode.DUPLICATE_CASH_FLOW_EXCLUDED.value,
                    severity=AlertSeverity.INFO,
                    message_key="planning.alert.duplicate_cash_flow_excluded",
                    related_resource_type=loser.source.resource_type,
                    related_resource_id=loser.source.resource_id,
                    date=loser.expected_at,
                    amount=loser.outstanding_amount,
                    currency=loser.currency,
                )
            )

        kept = tuple(winners[key] for key in order)
        alerts.extend(self._heuristic_alerts(kept))
        return DeduplicationResult(
            cash_flows=kept,
            excluded=tuple(excluded),
            alerts=tuple(alerts),
        )

    def _heuristic_alerts(
        self,
        cash_flows: tuple[PlanningCashFlow, ...],
    ) -> list[PlanningAlert]:
        alerts: list[PlanningAlert] = []
        for index, flow in enumerate(cash_flows):
            for other in cash_flows[index + 1 :]:
                if flow.direction is not other.direction:
                    continue
                if flow.currency != other.currency:
                    continue
                if flow.outstanding_amount != other.outstanding_amount:
                    continue
                if abs(flow.expected_at - other.expected_at) > HEURISTIC_DATE_WINDOW:
                    continue
                if flow.source_name == other.source_name:
                    continue
                alerts.append(
                    PlanningAlert(
                        code=PlanningAlertCode.POSSIBLE_DUPLICATE_CASH_FLOW.value,
                        severity=AlertSeverity.INFO,
                        message_key="planning.alert.possible_duplicate_cash_flow",
                        related_resource_type=other.source.resource_type,
                        related_resource_id=other.source.resource_id,
                        date=other.expected_at,
                        amount=other.outstanding_amount,
                        currency=other.currency,
                    )
                )
        return alerts
