"""Map PlanningSettings ↔ PlanningSettingsModel."""

from __future__ import annotations

from decimal import Decimal

from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.domain.enums.planning_horizon import PlanningHorizon
from wealthos.modules.planning.domain.enums.reservation import SafetyReserveStrategy
from wealthos.modules.planning.infrastructure.models.planning_projection_models import (
    PlanningSettingsModel,
)
from wealthos.shared.base import BaseMapper


class PlanningSettingsMapper(BaseMapper[PlanningSettingsModel, PlanningSettings]):
    def to_entity(self, model: PlanningSettingsModel) -> PlanningSettings:
        amount = (
            Decimal(str(model.safety_reserve_amount))
            if model.safety_reserve_amount is not None
            else None
        )
        return PlanningSettings(
            id=model.id,
            organization_id=model.organization_id,
            default_horizon=PlanningHorizon(model.default_horizon),
            safety_reserve_strategy=SafetyReserveStrategy(model.safety_reserve_strategy),
            safety_reserve_amount=amount,
            linked_emergency_goal_id=model.linked_emergency_goal_id,
            include_expected_income=model.include_expected_income,
            include_estimated_expenses=model.include_estimated_expenses,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: PlanningSettings) -> PlanningSettingsModel:
        return PlanningSettingsModel(
            id=entity.id,
            organization_id=entity.organization_id,
            default_horizon=entity.default_horizon.value,
            safety_reserve_strategy=entity.safety_reserve_strategy.value,
            safety_reserve_amount=entity.safety_reserve_amount,
            linked_emergency_goal_id=entity.linked_emergency_goal_id,
            include_expected_income=entity.include_expected_income,
            include_estimated_expenses=entity.include_estimated_expenses,
            version=entity.version,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def apply_to_model(
        self,
        entity: PlanningSettings,
        model: PlanningSettingsModel,
    ) -> PlanningSettingsModel:
        model.default_horizon = entity.default_horizon.value
        model.safety_reserve_strategy = entity.safety_reserve_strategy.value
        model.safety_reserve_amount = entity.safety_reserve_amount
        model.linked_emergency_goal_id = entity.linked_emergency_goal_id
        model.include_expected_income = entity.include_expected_income
        model.include_estimated_expenses = entity.include_estimated_expenses
        model.version = entity.version
        model.updated_at = entity.updated_at
        return model
