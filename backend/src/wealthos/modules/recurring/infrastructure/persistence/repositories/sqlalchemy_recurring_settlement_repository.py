"""SQLAlchemy RecurringSettlementRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.recurring.domain.entities.occurrence_settlement import (
    RecurringOccurrenceSettlement,
)
from wealthos.modules.recurring.infrastructure.persistence.mappers.recurring_aggregate_mapper import (
    RecurringAggregateMapper,
)
from wealthos.modules.recurring.infrastructure.persistence.models.recurring_models import (
    RecurringOccurrenceSettlementModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyRecurringSettlementRepository(
    BaseRepository[RecurringOccurrenceSettlementModel],
):
    def __init__(
        self,
        session: Session,
        mapper: RecurringAggregateMapper | None = None,
    ) -> None:
        super().__init__(session, RecurringOccurrenceSettlementModel)
        self._mapper = mapper or RecurringAggregateMapper()

    def add(
        self,
        settlement: RecurringOccurrenceSettlement,
    ) -> RecurringOccurrenceSettlement:
        model = self._mapper.settlement_to_model(settlement)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.settlement_to_entity(model)

    def list_for_occurrence(
        self,
        organization_id: UUID,
        occurrence_key: str,
        *,
        include_voided: bool = False,
    ) -> list[RecurringOccurrenceSettlement]:
        stmt = select(RecurringOccurrenceSettlementModel).where(
            RecurringOccurrenceSettlementModel.organization_id == organization_id,
            RecurringOccurrenceSettlementModel.occurrence_key == occurrence_key,
        )
        if not include_voided:
            stmt = stmt.where(RecurringOccurrenceSettlementModel.voided_at.is_(None))
        return [
            self._mapper.settlement_to_entity(model)
            for model in self.session.scalars(stmt)
        ]

    def list_for_keys(
        self,
        organization_id: UUID,
        occurrence_keys: tuple[str, ...],
        *,
        include_voided: bool = False,
    ) -> list[RecurringOccurrenceSettlement]:
        if not occurrence_keys:
            return []
        stmt = select(RecurringOccurrenceSettlementModel).where(
            RecurringOccurrenceSettlementModel.organization_id == organization_id,
            RecurringOccurrenceSettlementModel.occurrence_key.in_(occurrence_keys),
        )
        if not include_voided:
            stmt = stmt.where(RecurringOccurrenceSettlementModel.voided_at.is_(None))
        return [
            self._mapper.settlement_to_entity(model)
            for model in self.session.scalars(stmt)
        ]

    def get_by_id(
        self,
        organization_id: UUID,
        settlement_id: UUID,
    ) -> RecurringOccurrenceSettlement | None:
        stmt = select(RecurringOccurrenceSettlementModel).where(
            RecurringOccurrenceSettlementModel.organization_id == organization_id,
            RecurringOccurrenceSettlementModel.id == settlement_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.settlement_to_entity(model) if model else None

    def save(
        self,
        settlement: RecurringOccurrenceSettlement,
    ) -> RecurringOccurrenceSettlement:
        model = self.session.get(RecurringOccurrenceSettlementModel, settlement.id)
        if model is None or model.organization_id != settlement.organization_id:
            raise LookupError("Settlement not found for save.")
        model.voided_at = settlement.voided_at
        model.settled_amount = settlement.settled_amount
        model.link_type = settlement.link_type.value
        self.flush()
        self.refresh(model)
        return self._mapper.settlement_to_entity(model)
