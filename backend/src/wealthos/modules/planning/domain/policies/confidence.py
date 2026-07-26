"""Confidence label + reason codes — never a fake percentage (§23)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from wealthos.modules.planning.domain.enums.alert import PlanningAlertCode
from wealthos.modules.planning.domain.enums.cash_flow import CashFlowCertainty
from wealthos.modules.planning.domain.enums.projection import ProjectionConfidence
from wealthos.modules.planning.domain.enums.reservation import SafetyReserveStrategy
from wealthos.modules.planning.domain.enums.source import SourceStatus
from wealthos.modules.planning.domain.value_objects.alerts import PlanningSourceSummary
from wealthos.modules.planning.domain.value_objects.cash_flow import PlanningCashFlow

HIGH_THRESHOLD = 80
MEDIUM_THRESHOLD = 50

DEDUCTION_NO_RESERVE = 25
DEDUCTION_ESTIMATED_FLOWS = 15
DEDUCTION_EXPECTED_FLOWS = 10
DEDUCTION_SOURCE_PARTIAL = 15
DEDUCTION_SOURCE_UNAVAILABLE = 30
DEDUCTION_WARNINGS = 5


@dataclass(frozen=True, slots=True)
class ConfidenceAssessment:
    confidence: ProjectionConfidence
    score: int
    reasons: tuple[str, ...]


class ProjectionConfidencePolicy:
    """Explains reliability; it never silently rescales the amount."""

    def assess(
        self,
        *,
        included_flows: Iterable[PlanningCashFlow],
        sources: Iterable[PlanningSourceSummary],
        reserve_strategy: SafetyReserveStrategy,
        warning_count: int = 0,
    ) -> ConfidenceAssessment:
        score = 100
        reasons: list[str] = []
        capped_at_medium = False

        if reserve_strategy is SafetyReserveStrategy.NONE:
            score -= DEDUCTION_NO_RESERVE
            reasons.append(PlanningAlertCode.SAFETY_RESERVE_NOT_CONFIGURED.value)
            capped_at_medium = True

        certainties = {flow.certainty for flow in included_flows}
        if CashFlowCertainty.ESTIMATED in certainties:
            score -= DEDUCTION_ESTIMATED_FLOWS
            reasons.append("estimated_flows_included")
        if CashFlowCertainty.EXPECTED in certainties:
            score -= DEDUCTION_EXPECTED_FLOWS
            reasons.append("expected_flows_included")

        for source in sources:
            if source.status is SourceStatus.UNAVAILABLE:
                score -= DEDUCTION_SOURCE_UNAVAILABLE
                reasons.append(f"source_unavailable:{source.source_name}")
            elif source.status is SourceStatus.PARTIAL:
                score -= DEDUCTION_SOURCE_PARTIAL
                reasons.append(f"source_partial:{source.source_name}")

        if warning_count:
            score -= DEDUCTION_WARNINGS
            reasons.append("collection_warnings")

        score = max(score, 0)
        confidence = self._label(score)
        if capped_at_medium and confidence is ProjectionConfidence.HIGH:
            confidence = ProjectionConfidence.MEDIUM

        return ConfidenceAssessment(
            confidence=confidence,
            score=score,
            reasons=tuple(reasons),
        )

    def _label(self, score: int) -> ProjectionConfidence:
        if score >= HIGH_THRESHOLD:
            return ProjectionConfidence.HIGH
        if score >= MEDIUM_THRESHOLD:
            return ProjectionConfidence.MEDIUM
        return ProjectionConfidence.LOW
