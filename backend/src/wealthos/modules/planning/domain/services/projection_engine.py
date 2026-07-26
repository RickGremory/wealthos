"""calculate_projection(context) → PlanningProjectionResult (SPEC-004 §6).

Pure and deterministic: the same ``PlanningContext`` always yields the same
result. No wall clock, no repositories, no foreign ORM.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from wealthos.modules.planning.domain.enums.alert import (
    AlertSeverity,
    PlanningAlertCode,
)
from wealthos.modules.planning.domain.enums.cash_flow import CashFlowDirection
from wealthos.modules.planning.domain.enums.projection import (
    ProjectionConfidence,
    ProjectionStatus,
)
from wealthos.modules.planning.domain.enums.source import PlanningSource, SourceStatus
from wealthos.modules.planning.domain.policies.account_eligibility import (
    AccountEligibilityPolicy,
)
from wealthos.modules.planning.domain.policies.cash_flow_inclusion import (
    CashFlowInclusionPolicy,
)
from wealthos.modules.planning.domain.policies.confidence import ProjectionConfidencePolicy
from wealthos.modules.planning.domain.policies.event_ordering import order_events
from wealthos.modules.planning.domain.policies.safe_to_spend import (
    SafeToSpendOutcome,
    SafeToSpendPolicy,
)
from wealthos.modules.planning.domain.policies.safety_reserve import SafetyReservePolicy
from wealthos.modules.planning.domain.policies.status import ProjectionStatusPolicy
from wealthos.modules.planning.domain.services.deduplicator import (
    PlanningCashFlowDeduplicator,
)
from wealthos.modules.planning.domain.services.projection_explainer import (
    PlanningProjectionExplainer,
)
from wealthos.modules.planning.domain.services.settlement_reconciler import (
    PlanningSettlementReconciler,
)
from wealthos.modules.planning.domain.value_objects.alerts import (
    ExcludedPlanningItem,
    PlanningAlert,
    PlanningBreakdownItem,
)
from wealthos.modules.planning.domain.value_objects.cash_flow import PlanningCashFlow
from wealthos.modules.planning.domain.value_objects.money_utils import ZERO, quantize_money
from wealthos.modules.planning.domain.value_objects.projection_point import ProjectionPoint
from wealthos.modules.planning.domain.value_objects.projection_result import (
    PlanningContext,
    PlanningProjectionResult,
)
from wealthos.modules.planning.domain.value_objects.reservation import SafetyReserveResult


@dataclass(frozen=True, slots=True)
class _Trough:
    minimum: Decimal
    minimum_at: datetime
    ending: Decimal


class PlanningProjectionEngine:
    def __init__(
        self,
        *,
        eligibility: AccountEligibilityPolicy | None = None,
        deduplicator: PlanningCashFlowDeduplicator | None = None,
        reconciler: PlanningSettlementReconciler | None = None,
        reserve_policy: SafetyReservePolicy | None = None,
        safe_to_spend: SafeToSpendPolicy | None = None,
        status_policy: ProjectionStatusPolicy | None = None,
        confidence_policy: ProjectionConfidencePolicy | None = None,
        explainer: PlanningProjectionExplainer | None = None,
    ) -> None:
        self._eligibility = eligibility or AccountEligibilityPolicy()
        self._deduplicator = deduplicator or PlanningCashFlowDeduplicator()
        self._reconciler = reconciler or PlanningSettlementReconciler()
        self._reserve_policy = reserve_policy or SafetyReservePolicy()
        self._safe_to_spend = safe_to_spend or SafeToSpendPolicy()
        self._status_policy = status_policy or ProjectionStatusPolicy()
        self._confidence_policy = confidence_policy or ProjectionConfidencePolicy()
        self._explainer = explainer or PlanningProjectionExplainer()

    def calculate(self, context: PlanningContext) -> PlanningProjectionResult:
        currency = context.currency.strip().upper()

        eligible_accounts = self._eligibility.eligible(context.accounts, currency=currency)
        current_cash = self._eligibility.current_available_cash(
            context.accounts,
            currency=currency,
        )

        deduped = self._deduplicator.deduplicate(context.cash_flows)
        reconciled = self._reconciler.reconcile(deduped.cash_flows, context.settlements)

        inclusion = CashFlowInclusionPolicy(
            include_expected_income=context.settings.include_expected_income,
            include_estimated_expenses=context.settings.include_estimated_expenses,
        )
        included: list[PlanningCashFlow] = []
        excluded: list[ExcludedPlanningItem] = list(deduped.excluded)
        for flow in reconciled.cash_flows:
            decision = inclusion.decide(flow, period=context.period, currency=currency)
            if decision.included:
                included.append(flow)
                continue
            excluded.append(
                ExcludedPlanningItem(
                    occurrence_key=flow.occurrence_key,
                    label=flow.label,
                    reason_code=decision.reason_code or "excluded",
                    amount=flow.outstanding_amount,
                    currency=flow.currency,
                    date=flow.expected_at,
                    source_name=flow.source_name,
                )
            )

        ordered = order_events(included)
        timeline = self._build_timeline(context, current_cash, ordered)
        trough = self._find_trough(timeline)

        reserve = self._reserve_policy.resolve(context.settings, context.reservations)
        other_reserved = self._reserve_policy.other_reserved_funds(
            context.reservations,
            currency=currency,
            exclude_key=reserve.source_reservation_key,
        )
        required_minimum = quantize_money(reserve.required_amount + other_reserved)

        outcome = self._safe_to_spend.calculate(
            minimum_projected_balance=trough.minimum,
            required_reserve=required_minimum,
        )

        critical_unavailable = self._accounts_source_unavailable(context)
        status = self._status_policy.resolve(
            outcome=outcome,
            eligible_cash=current_cash,
            has_eligible_accounts=bool(eligible_accounts),
            critical_source_unavailable=critical_unavailable,
        )
        computable = status.is_computable

        confidence_assessment = self._confidence_policy.assess(
            included_flows=ordered,
            sources=context.sources,
            reserve_strategy=reserve.strategy,
            warning_count=len(context.warnings),
        )
        confidence = (
            confidence_assessment.confidence if computable else ProjectionConfidence.LOW
        )

        expected_income = _sum_direction(ordered, CashFlowDirection.INFLOW)
        committed_outflows = _sum_direction(ordered, CashFlowDirection.OUTFLOW)

        deficit_at = self._first_breach(timeline, required_minimum) if computable else None

        alerts = self._build_alerts(
            context=context,
            reserve=reserve,
            outcome=outcome,
            status=status,
            confidence=confidence,
            deficit_at=deficit_at,
            currency=currency,
            dedupe_alerts=deduped.alerts,
        )

        breakdown = self._build_breakdown(
            context=context,
            currency=currency,
            current_cash=current_cash,
            included=ordered,
            excluded=tuple(excluded),
            reserve=reserve,
        )

        explanation = self._explainer.explain(
            timeline=timeline,
            required_reserve=required_minimum,
            minimum_balance=trough.minimum if computable else None,
            minimum_balance_at=trough.minimum_at if computable else None,
            outcome=outcome if computable else None,
        )

        return PlanningProjectionResult(
            organization_id=context.organization_id,
            currency=currency,
            horizon=context.period.horizon,
            period=context.period,
            calculated_at=context.calculated_at,
            current_available_cash=current_cash,
            expected_income=expected_income,
            committed_outflows=committed_outflows,
            reserved_funds=other_reserved,
            required_safety_reserve=reserve.required_amount,
            required_minimum_balance=required_minimum,
            minimum_projected_balance=trough.minimum if computable else None,
            minimum_balance_at=trough.minimum_at if computable else None,
            projected_ending_balance=trough.ending if computable else None,
            safe_to_spend=outcome.safe_to_spend if computable else None,
            cash_deficit=outcome.cash_deficit if computable else None,
            reserve_shortfall=outcome.reserve_shortfall if computable else None,
            deficit_at=deficit_at,
            status=status,
            confidence=confidence,
            confidence_reasons=confidence_assessment.reasons,
            timeline=timeline if computable else (),
            breakdown=breakdown,
            alerts=alerts,
            excluded_items=tuple(excluded),
            sources=context.sources,
            accounts=context.accounts,
            included_cash_flows=ordered,
            explanation=explanation,
        )

    def _build_timeline(
        self,
        context: PlanningContext,
        current_cash: Decimal,
        ordered: tuple[PlanningCashFlow, ...],
    ) -> tuple[ProjectionPoint, ...]:
        points = [
            ProjectionPoint(
                at=context.period.start,
                label="planning.timeline.current_cash",
                delta=current_cash,
                balance=current_cash,
                category="current_cash",
            )
        ]
        balance = current_cash
        for flow in ordered:
            balance = quantize_money(balance + flow.signed_outstanding)
            points.append(
                ProjectionPoint(
                    at=flow.expected_at,
                    label=flow.label,
                    delta=flow.signed_outstanding,
                    balance=balance,
                    flow_id=flow.id,
                    occurrence_key=flow.occurrence_key,
                    direction=flow.direction,
                    certainty=flow.certainty,
                    category=flow.category,
                    source_name=flow.source_name,
                )
            )
        return tuple(points)

    def _find_trough(self, timeline: tuple[ProjectionPoint, ...]) -> _Trough:
        """The period minimum — including t0 — is what constrains spending."""
        minimum = timeline[0].balance
        minimum_at = timeline[0].at
        for point in timeline[1:]:
            if point.balance < minimum:
                minimum = point.balance
                minimum_at = point.at
        return _Trough(
            minimum=minimum,
            minimum_at=minimum_at,
            ending=timeline[-1].balance,
        )

    def _first_breach(
        self,
        timeline: tuple[ProjectionPoint, ...],
        required_minimum: Decimal,
    ) -> datetime | None:
        for point in timeline:
            if point.balance < required_minimum:
                return point.at
        return None

    def _accounts_source_unavailable(self, context: PlanningContext) -> bool:
        return any(
            source.source_name == PlanningSource.ACCOUNTS.value
            and source.status is SourceStatus.UNAVAILABLE
            for source in context.sources
        )

    def _build_alerts(
        self,
        *,
        context: PlanningContext,
        reserve: SafetyReserveResult,
        outcome: SafeToSpendOutcome,
        status: ProjectionStatus,
        confidence: ProjectionConfidence,
        deficit_at: datetime | None,
        currency: str,
        dedupe_alerts: tuple[PlanningAlert, ...],
    ) -> tuple[PlanningAlert, ...]:
        alerts: list[PlanningAlert] = []

        if status is ProjectionStatus.INSUFFICIENT_DATA:
            alerts.append(
                PlanningAlert(
                    code=PlanningAlertCode.NO_ELIGIBLE_ACCOUNTS.value,
                    severity=AlertSeverity.CRITICAL,
                    message_key="planning.alert.no_eligible_accounts",
                    currency=currency,
                )
            )

        for code in reserve.reason_codes:
            alerts.append(
                PlanningAlert(
                    code=code,
                    severity=AlertSeverity.WARNING,
                    message_key=f"planning.alert.{code}",
                    currency=currency,
                )
            )

        if status.is_computable and outcome.cash_deficit is not None:
            alerts.append(
                PlanningAlert(
                    code=PlanningAlertCode.PROJECTED_DEFICIT.value,
                    severity=AlertSeverity.CRITICAL,
                    message_key="planning.alert.projected_deficit",
                    date=deficit_at,
                    amount=outcome.cash_deficit,
                    currency=currency,
                )
            )

        if status.is_computable and outcome.reserve_shortfall is not None:
            alerts.append(
                PlanningAlert(
                    code=PlanningAlertCode.RESERVE_SHORTFALL.value,
                    severity=AlertSeverity.WARNING,
                    message_key="planning.alert.reserve_shortfall",
                    date=deficit_at,
                    amount=outcome.reserve_shortfall,
                    currency=currency,
                )
            )

        for source in context.sources:
            if source.status is SourceStatus.UNAVAILABLE:
                alerts.append(
                    PlanningAlert(
                        code=PlanningAlertCode.SOURCE_UNAVAILABLE.value,
                        severity=AlertSeverity.WARNING,
                        message_key="planning.alert.source_unavailable",
                        related_resource_type="planning_source",
                        related_resource_id=source.source_name,
                    )
                )
            elif source.status is SourceStatus.PARTIAL:
                alerts.append(
                    PlanningAlert(
                        code=PlanningAlertCode.SOURCE_PARTIAL.value,
                        severity=AlertSeverity.INFO,
                        message_key="planning.alert.source_partial",
                        related_resource_type="planning_source",
                        related_resource_id=source.source_name,
                    )
                )

        alerts.extend(dedupe_alerts)

        if confidence is ProjectionConfidence.LOW and status.is_computable:
            alerts.append(
                PlanningAlert(
                    code=PlanningAlertCode.LOW_PROJECTION_CONFIDENCE.value,
                    severity=AlertSeverity.INFO,
                    message_key="planning.alert.low_projection_confidence",
                )
            )

        return tuple(alerts)

    def _build_breakdown(
        self,
        *,
        context: PlanningContext,
        currency: str,
        current_cash: Decimal,
        included: tuple[PlanningCashFlow, ...],
        excluded: tuple[ExcludedPlanningItem, ...],
        reserve: SafetyReserveResult,
    ) -> tuple[PlanningBreakdownItem, ...]:
        items = [
            PlanningBreakdownItem(
                id="current_cash",
                category="current_cash",
                label="planning.breakdown.current_cash",
                amount=current_cash,
                currency=currency,
                date=context.period.start,
                direction="add",
                source_name=PlanningSource.ACCOUNTS.value,
                source_id=None,
                certainty=None,
                included=True,
            )
        ]

        for flow in included:
            items.append(
                PlanningBreakdownItem(
                    id=flow.id,
                    category=flow.category,
                    label=flow.label,
                    amount=flow.outstanding_amount,
                    currency=flow.currency,
                    date=flow.expected_at,
                    direction="add" if flow.direction is CashFlowDirection.INFLOW else "subtract",
                    source_name=flow.source_name,
                    source_id=flow.source.resource_id,
                    certainty=flow.certainty,
                    included=True,
                )
            )

        for reservation in context.reservations:
            if reservation.currency.strip().upper() != currency:
                continue
            if reservation.occurrence_key == reserve.source_reservation_key:
                continue
            items.append(
                PlanningBreakdownItem(
                    id=reservation.id,
                    category=reservation.reservation_type.value,
                    label=reservation.label,
                    amount=reservation.outstanding_amount,
                    currency=reservation.currency,
                    date=reservation.effective_at,
                    direction="subtract",
                    source_name=reservation.source.source_name,
                    source_id=reservation.source.resource_id,
                    certainty=None,
                    included=True,
                )
            )

        if reserve.required_amount > ZERO:
            items.append(
                PlanningBreakdownItem(
                    id="safety_reserve",
                    category="safety_reserve",
                    label=reserve.label,
                    amount=reserve.required_amount,
                    currency=currency,
                    date=None,
                    direction="subtract",
                    source_name="planning",
                    source_id=None,
                    certainty=None,
                    included=True,
                )
            )

        for item in excluded:
            items.append(
                PlanningBreakdownItem(
                    id=item.occurrence_key,
                    category="excluded",
                    label=item.label,
                    amount=item.amount,
                    currency=item.currency,
                    date=item.date,
                    direction="subtract",
                    source_name=item.source_name,
                    source_id=None,
                    certainty=None,
                    included=False,
                    exclusion_reason=item.reason_code,
                )
            )

        return tuple(items)


def _sum_direction(
    flows: tuple[PlanningCashFlow, ...],
    direction: CashFlowDirection,
) -> Decimal:
    total = ZERO
    for flow in flows:
        if flow.direction is direction:
            total += flow.outstanding_amount
    return quantize_money(total)
