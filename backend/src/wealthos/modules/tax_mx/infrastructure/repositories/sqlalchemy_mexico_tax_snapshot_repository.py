"""SQLAlchemy MexicoTaxSnapshotRepository."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import (
    MexicoTaxCalculationSnapshotModel,
)


class SqlAlchemyMexicoTaxSnapshotRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        *,
        organization_id: UUID,
        tax_calculation_id: UUID,
        configuration_version: int,
        catalog_version: str,
        calculation_engine: str,
        calculation_engine_version: str,
        transaction_cutoff_at: datetime,
        workpaper_json: dict[str, Any],
    ) -> UUID:
        snapshot_id = uuid4()
        self._session.add(
            MexicoTaxCalculationSnapshotModel(
                id=snapshot_id,
                organization_id=organization_id,
                tax_calculation_id=tax_calculation_id,
                configuration_version=configuration_version,
                catalog_version=catalog_version,
                calculation_engine=calculation_engine,
                calculation_engine_version=calculation_engine_version,
                transaction_cutoff_at=transaction_cutoff_at,
                workpaper_json=workpaper_json,
            )
        )
        self._session.flush()
        return snapshot_id

    def get_by_calculation(
        self, organization_id: UUID, tax_calculation_id: UUID
    ) -> dict[str, Any] | None:
        stmt = select(MexicoTaxCalculationSnapshotModel).where(
            MexicoTaxCalculationSnapshotModel.organization_id == organization_id,
            MexicoTaxCalculationSnapshotModel.tax_calculation_id == tax_calculation_id,
        )
        model = self._session.scalars(stmt).first()
        return model.workpaper_json if model else None

    def get_latest_for_period_via_calculations(
        self, organization_id: UUID, tax_calculation_ids: list[UUID]
    ) -> dict[str, Any] | None:
        if not tax_calculation_ids:
            return None
        stmt = (
            select(MexicoTaxCalculationSnapshotModel)
            .where(
                MexicoTaxCalculationSnapshotModel.organization_id == organization_id,
                MexicoTaxCalculationSnapshotModel.tax_calculation_id.in_(tax_calculation_ids),
            )
            .order_by(MexicoTaxCalculationSnapshotModel.created_at.desc())
            .limit(1)
        )
        model = self._session.scalars(stmt).first()
        return model.workpaper_json if model else None
