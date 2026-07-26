"""Map PlannedCashFlow ↔ PlannedCashFlowModel."""

from __future__ import annotations

from wealthos.modules.planning.domain.entities.planned_cash_flow import PlannedCashFlow
from wealthos.modules.planning.domain.enums.cash_flow import (
    CashFlowCertainty,
    CashFlowDirection,
    CashFlowStatus,
)
from wealthos.modules.planning.infrastructure.models.planning_projection_models import (
    PlannedCashFlowModel,
)
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class PlannedCashFlowMapper(BaseMapper[PlannedCashFlowModel, PlannedCashFlow]):
    def to_entity(self, model: PlannedCashFlowModel) -> PlannedCashFlow:
        return PlannedCashFlow(
            id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            direction=CashFlowDirection(model.direction),
            amount=Money(model.amount, model.currency),
            expected_at=model.expected_at,
            certainty=CashFlowCertainty(model.certainty),
            status=CashFlowStatus(model.status),
            notes=model.notes,
            settled_transaction_id=model.settled_transaction_id,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: PlannedCashFlow) -> PlannedCashFlowModel:
        return PlannedCashFlowModel(
            id=entity.id,
            organization_id=entity.organization_id,
            name=entity.name,
            direction=entity.direction.value,
            amount=entity.amount.amount,
            currency=entity.amount.currency.value,
            expected_at=entity.expected_at,
            certainty=entity.certainty.value,
            status=entity.status.value,
            notes=entity.notes,
            settled_transaction_id=entity.settled_transaction_id,
            version=entity.version,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def apply_to_model(
        self,
        entity: PlannedCashFlow,
        model: PlannedCashFlowModel,
    ) -> PlannedCashFlowModel:
        model.name = entity.name
        model.direction = entity.direction.value
        model.amount = entity.amount.amount
        model.currency = entity.amount.currency.value
        model.expected_at = entity.expected_at
        model.certainty = entity.certainty.value
        model.status = entity.status.value
        model.notes = entity.notes
        model.settled_transaction_id = entity.settled_transaction_id
        model.version = entity.version
        model.updated_at = entity.updated_at
        return model
