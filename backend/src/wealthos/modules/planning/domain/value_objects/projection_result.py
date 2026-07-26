"""PlanningContext in, PlanningProjectionResult out — the whole engine contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.domain.enums.planning_horizon import PlanningHorizon
from wealthos.modules.planning.domain.enums.projection import (
    ProjectionConfidence,
    ProjectionStatus,
)
from wealthos.modules.planning.domain.value_objects.account_snapshot import (
    PlanningAccountSnapshot,
)
from wealthos.modules.planning.domain.value_objects.alerts import (
    ExcludedPlanningItem,
    PlanningAlert,
    PlanningBreakdownItem,
    PlanningExplanation,
    PlanningSourceSummary,
)
from wealthos.modules.planning.domain.value_objects.cash_flow import PlanningCashFlow
from wealthos.modules.planning.domain.value_objects.collection_warning import (
    PlanningCollectionWarning,
)
from wealthos.modules.planning.domain.value_objects.projection_point import ProjectionPoint
from wealthos.modules.planning.domain.value_objects.reservation import PlanningReservation
from wealthos.modules.planning.domain.value_objects.settlement import PlanningSettlement


@dataclass(frozen=True, slots=True)
class ProjectionPeriod:
    """Resolved window in the org timezone. 30 days is never "end of month"."""

    horizon: PlanningHorizon
    start: datetime
    end: datetime
    start_date: date
    end_date: date
    timezone: str

    def contains(self, moment: datetime) -> bool:
        return self.start <= moment <= self.end


@dataclass(frozen=True, slots=True)
class PlanningContext:
    """Everything the pure engine may read. No repos, no clock, no HTTP."""

    organization_id: UUID
    currency: str
    calculated_at: datetime
    period: ProjectionPeriod
    settings: PlanningSettings
    accounts: tuple[PlanningAccountSnapshot, ...] = ()
    cash_flows: tuple[PlanningCashFlow, ...] = ()
    reservations: tuple[PlanningReservation, ...] = ()
    settlements: tuple[PlanningSettlement, ...] = ()
    sources: tuple[PlanningSourceSummary, ...] = ()
    warnings: tuple[PlanningCollectionWarning, ...] = ()

    @property
    def horizon(self) -> PlanningHorizon:
        return self.period.horizon


@dataclass(frozen=True, slots=True)
class PlanningProjectionResult:
    """Safe To Spend is one field among many — never a stored ledger value."""

    organization_id: UUID
    currency: str
    horizon: PlanningHorizon
    period: ProjectionPeriod
    calculated_at: datetime

    current_available_cash: Decimal
    expected_income: Decimal
    committed_outflows: Decimal
    reserved_funds: Decimal
    required_safety_reserve: Decimal
    required_minimum_balance: Decimal

    minimum_projected_balance: Decimal | None
    minimum_balance_at: datetime | None
    projected_ending_balance: Decimal | None

    safe_to_spend: Decimal | None
    cash_deficit: Decimal | None
    reserve_shortfall: Decimal | None
    deficit_at: datetime | None

    status: ProjectionStatus
    confidence: ProjectionConfidence
    confidence_reasons: tuple[str, ...]

    timeline: tuple[ProjectionPoint, ...]
    breakdown: tuple[PlanningBreakdownItem, ...]
    alerts: tuple[PlanningAlert, ...]
    excluded_items: tuple[ExcludedPlanningItem, ...]
    sources: tuple[PlanningSourceSummary, ...]
    accounts: tuple[PlanningAccountSnapshot, ...]
    included_cash_flows: tuple[PlanningCashFlow, ...]
    explanation: PlanningExplanation
