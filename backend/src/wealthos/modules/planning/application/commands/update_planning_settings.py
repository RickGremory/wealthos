"""Update org Planning settings (get-or-create on first write)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.domain.exceptions import (
    LinkedResourceNotFound,
    PlanningVersionConflict,
)
from wealthos.modules.planning.domain.ports.repositories import PlanningSettingsRepository
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


@dataclass(frozen=True, slots=True)
class UpdatePlanningSettingsInput:
    organization_id: UUID
    expected_version: int | None
    default_horizon: str
    safety_reserve_strategy: str
    safety_reserve_amount: Decimal | None
    linked_emergency_goal_id: UUID | None
    include_expected_income: bool
    include_estimated_expenses: bool


class UpdatePlanningSettingsCommand:
    def __init__(
        self,
        settings: PlanningSettingsRepository,
        goals: GoalRepository,
        uow: SqlAlchemyUnitOfWork,
    ) -> None:
        self._settings = settings
        self._goals = goals
        self._uow = uow

    def execute(self, data: UpdatePlanningSettingsInput) -> PlanningSettings:
        if data.linked_emergency_goal_id is not None:
            goal = self._goals.get_by_id(
                data.organization_id,
                data.linked_emergency_goal_id,
            )
            if goal is None:
                raise LinkedResourceNotFound("Linked emergency goal not found.")

        existing = self._settings.get_by_organization(data.organization_id)
        if existing is None:
            created = PlanningSettings.create(
                organization_id=data.organization_id,
                default_horizon=data.default_horizon,
                safety_reserve_strategy=data.safety_reserve_strategy,
                safety_reserve_amount=data.safety_reserve_amount,
                linked_emergency_goal_id=data.linked_emergency_goal_id,
                include_expected_income=data.include_expected_income,
                include_estimated_expenses=data.include_estimated_expenses,
            )
            saved = self._settings.add(created)
            self._uow.commit()
            return saved

        if data.expected_version is not None and existing.version != data.expected_version:
            raise PlanningVersionConflict("Planning settings were modified by another request.")

        existing.update(
            default_horizon=data.default_horizon,
            safety_reserve_strategy=data.safety_reserve_strategy,
            safety_reserve_amount=data.safety_reserve_amount,
            linked_emergency_goal_id=data.linked_emergency_goal_id,
            include_expected_income=data.include_expected_income,
            include_estimated_expenses=data.include_estimated_expenses,
        )
        saved = self._settings.save(existing)
        self._uow.commit()
        return saved
