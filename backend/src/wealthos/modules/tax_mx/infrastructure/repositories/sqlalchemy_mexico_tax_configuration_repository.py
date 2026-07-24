"""SQLAlchemy MexicoTaxConfigurationRepository."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from wealthos.modules.tax_mx.domain.entities.mexico_tax_configuration import (
    MexicoTaxConfiguration,
)
from wealthos.modules.tax_mx.infrastructure.mappers.mexico_tax_configuration_mapper import (
    MexicoTaxConfigurationMapper,
)
from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import (
    MexicoTaxConfigurationModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyMexicoTaxConfigurationRepository(BaseRepository[MexicoTaxConfigurationModel]):
    def __init__(
        self, session: Session, mapper: MexicoTaxConfigurationMapper | None = None
    ) -> None:
        super().__init__(session, MexicoTaxConfigurationModel)
        self._mapper = mapper or MexicoTaxConfigurationMapper()

    def add(self, configuration: MexicoTaxConfiguration) -> MexicoTaxConfiguration:
        model = self._mapper.to_model(configuration)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(
        self, organization_id: UUID, configuration_id: UUID
    ) -> MexicoTaxConfiguration | None:
        stmt = select(MexicoTaxConfigurationModel).where(
            MexicoTaxConfigurationModel.organization_id == organization_id,
            MexicoTaxConfigurationModel.id == configuration_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def get_applicable(
        self, tax_profile_id: UUID, target_date: date
    ) -> MexicoTaxConfiguration | None:
        stmt = (
            select(MexicoTaxConfigurationModel)
            .where(
                MexicoTaxConfigurationModel.tax_profile_id == tax_profile_id,
                MexicoTaxConfigurationModel.effective_from <= target_date,
                or_(
                    MexicoTaxConfigurationModel.effective_to.is_(None),
                    MexicoTaxConfigurationModel.effective_to >= target_date,
                ),
            )
            .order_by(MexicoTaxConfigurationModel.version.desc())
            .limit(1)
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def get_current(self, tax_profile_id: UUID) -> MexicoTaxConfiguration | None:
        stmt = (
            select(MexicoTaxConfigurationModel)
            .where(
                MexicoTaxConfigurationModel.tax_profile_id == tax_profile_id,
                MexicoTaxConfigurationModel.effective_to.is_(None),
            )
            .order_by(MexicoTaxConfigurationModel.version.desc())
            .limit(1)
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_versions(self, tax_profile_id: UUID) -> list[MexicoTaxConfiguration]:
        stmt = (
            select(MexicoTaxConfigurationModel)
            .where(MexicoTaxConfigurationModel.tax_profile_id == tax_profile_id)
            .order_by(MexicoTaxConfigurationModel.version.desc())
        )
        return [self._mapper.to_entity(m) for m in self.session.scalars(stmt)]

    def get_next_version(self, tax_profile_id: UUID) -> int:
        stmt = select(func.coalesce(func.max(MexicoTaxConfigurationModel.version), 0)).where(
            MexicoTaxConfigurationModel.tax_profile_id == tax_profile_id
        )
        return int(self.session.scalar(stmt) or 0) + 1

    def save(self, configuration: MexicoTaxConfiguration) -> MexicoTaxConfiguration:
        model = self.session.get(MexicoTaxConfigurationModel, configuration.id)
        if model is None:
            raise LookupError("Configuration not found for save.")
        self._mapper.apply_to_model(configuration, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def has_overlap(
        self,
        tax_profile_id: UUID,
        effective_from: date,
        effective_to: date | None,
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        # Overlap when existing.from <= new.to (or open) and existing.to is open
        # or existing.to >= new.from.
        end = effective_to
        conditions = [
            MexicoTaxConfigurationModel.tax_profile_id == tax_profile_id,
            MexicoTaxConfigurationModel.effective_from <= (end if end is not None else date.max),
            or_(
                MexicoTaxConfigurationModel.effective_to.is_(None),
                MexicoTaxConfigurationModel.effective_to >= effective_from,
            ),
        ]
        if exclude_id is not None:
            conditions.append(MexicoTaxConfigurationModel.id != exclude_id)
        stmt = select(MexicoTaxConfigurationModel.id).where(and_(*conditions)).limit(1)
        return self.session.scalars(stmt).first() is not None
