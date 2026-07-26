"""SQLAlchemy PlanningSettingsRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.infrastructure.mappers.planning_settings_mapper import (
    PlanningSettingsMapper,
)
from wealthos.modules.planning.infrastructure.models.planning_projection_models import (
    PlanningSettingsModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyPlanningSettingsRepository(BaseRepository[PlanningSettingsModel]):
    def __init__(
        self,
        session: Session,
        mapper: PlanningSettingsMapper | None = None,
    ) -> None:
        super().__init__(session, PlanningSettingsModel)
        self._mapper = mapper or PlanningSettingsMapper()

    def get_by_organization(self, organization_id: UUID) -> PlanningSettings | None:
        stmt = select(PlanningSettingsModel).where(
            PlanningSettingsModel.organization_id == organization_id
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def add(self, settings: PlanningSettings) -> PlanningSettings:
        model = self._mapper.to_model(settings)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def save(self, settings: PlanningSettings) -> PlanningSettings:
        model = self.session.get(PlanningSettingsModel, settings.id)
        if model is None or model.organization_id != settings.organization_id:
            raise LookupError("Planning settings not found for save.")
        self._mapper.apply_to_model(settings, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)
