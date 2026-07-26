"""Persistence ports for the only two Planning-owned tables."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from wealthos.modules.planning.domain.entities.planned_cash_flow import PlannedCashFlow
from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings


class PlanningSettingsRepository(Protocol):
    """One row per organization."""

    def get_by_organization(self, organization_id: UUID) -> PlanningSettings | None: ...

    def add(self, settings: PlanningSettings) -> PlanningSettings: ...

    def save(self, settings: PlanningSettings) -> PlanningSettings: ...


class PlannedCashFlowRepository(Protocol):
    def add(self, cash_flow: PlannedCashFlow) -> PlannedCashFlow: ...

    def get_by_id(
        self,
        organization_id: UUID,
        cash_flow_id: UUID,
    ) -> PlannedCashFlow | None: ...

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        currency: str | None = None,
        status: str | None = None,
        direction: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> list[PlannedCashFlow]: ...

    def list_active_in_period(
        self,
        organization_id: UUID,
        *,
        currency: str,
        period_start: datetime,
        period_end: datetime,
    ) -> list[PlannedCashFlow]: ...

    def save(self, cash_flow: PlannedCashFlow) -> PlannedCashFlow: ...
