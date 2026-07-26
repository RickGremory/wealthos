"""Build and calculate the Financial Projection for an org."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationRepository,
)
from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.domain.enums.planning_horizon import PlanningHorizon
from wealthos.modules.planning.domain.ports.repositories import PlanningSettingsRepository
from wealthos.modules.planning.domain.services.context_builder import PlanningContextBuilder
from wealthos.modules.planning.domain.services.horizon_resolver import (
    PlanningHorizonResolver,
)
from wealthos.modules.planning.domain.services.projection_engine import (
    PlanningProjectionEngine,
)
from wealthos.modules.planning.domain.value_objects.projection_result import (
    PlanningContext,
    PlanningProjectionResult,
)


@dataclass(frozen=True, slots=True)
class GetPlanningProjectionInput:
    organization_id: UUID
    currency: str
    horizon: str | None = None
    calculated_at: datetime | None = None


class GetPlanningProjectionQuery:
    def __init__(
        self,
        organizations: OrganizationRepository,
        settings: PlanningSettingsRepository,
        context_builder: PlanningContextBuilder,
        horizon_resolver: PlanningHorizonResolver | None = None,
        engine: PlanningProjectionEngine | None = None,
    ) -> None:
        self._organizations = organizations
        self._settings = settings
        self._context_builder = context_builder
        self._horizon_resolver = horizon_resolver or PlanningHorizonResolver()
        self._engine = engine or PlanningProjectionEngine()

    def execute(self, data: GetPlanningProjectionInput) -> PlanningProjectionResult:
        context = self.build_context(data)
        return self._engine.calculate(context)

    def build_context(self, data: GetPlanningProjectionInput) -> PlanningContext:
        org = self._organizations.get_by_id(data.organization_id)
        timezone = org.timezone.value if org is not None else "UTC"
        settings = self._settings.get_by_organization(data.organization_id)
        if settings is None:
            settings = PlanningSettings.defaults(data.organization_id)

        calculated_at = data.calculated_at or datetime.now(UTC)
        horizon = data.horizon or settings.default_horizon.value
        period = self._horizon_resolver.resolve(
            horizon=horizon,
            timezone=timezone,
            calculated_at=calculated_at,
        )
        return self._context_builder.build(
            period=period,
            settings=settings,
            calculated_at=calculated_at,
            currency=data.currency,
        )


@dataclass(frozen=True, slots=True)
class GetSafeToSpendSummary:
    organization_id: UUID
    currency: str
    horizon: PlanningHorizon
    safe_to_spend: str | None
    status: str
    confidence: str
    reserve_shortfall: str
    cash_deficit: str
    lowest_balance_at: str | None
    calculated_at: str


class GetSafeToSpendSummaryQuery:
    def __init__(self, projection: GetPlanningProjectionQuery) -> None:
        self._projection = projection

    def execute(self, data: GetPlanningProjectionInput) -> GetSafeToSpendSummary:
        result = self._projection.execute(data)
        return GetSafeToSpendSummary(
            organization_id=result.organization_id,
            currency=result.currency,
            horizon=result.horizon,
            safe_to_spend=_money_str(result.safe_to_spend),
            status=result.status.value,
            confidence=result.confidence.value,
            reserve_shortfall=_money_str(result.reserve_shortfall) or "0.00",
            cash_deficit=_money_str(result.cash_deficit) or "0.00",
            lowest_balance_at=(
                result.minimum_balance_at.isoformat() if result.minimum_balance_at else None
            ),
            calculated_at=result.calculated_at.isoformat(),
        )


def _money_str(value) -> str | None:
    if value is None:
        return None
    return f"{value:.2f}"
