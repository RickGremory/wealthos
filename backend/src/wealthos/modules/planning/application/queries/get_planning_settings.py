"""Read Planning settings (defaults when never configured)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.domain.ports.repositories import PlanningSettingsRepository


@dataclass(frozen=True, slots=True)
class GetPlanningSettingsInput:
    organization_id: UUID


class GetPlanningSettingsQuery:
    def __init__(self, settings: PlanningSettingsRepository) -> None:
        self._settings = settings

    def execute(self, data: GetPlanningSettingsInput) -> PlanningSettings:
        existing = self._settings.get_by_organization(data.organization_id)
        return existing or PlanningSettings.defaults(data.organization_id)
