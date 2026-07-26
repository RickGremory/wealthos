"""Cancel (logical delete) a planned cash flow."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.planning.domain.entities.planned_cash_flow import PlannedCashFlow
from wealthos.modules.planning.domain.exceptions import PlannedCashFlowNotFoundError
from wealthos.modules.planning.domain.ports.repositories import PlannedCashFlowRepository
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


@dataclass(frozen=True, slots=True)
class CancelPlannedCashFlowInput:
    organization_id: UUID
    cash_flow_id: UUID


class CancelPlannedCashFlowCommand:
    def __init__(
        self,
        planned: PlannedCashFlowRepository,
        uow: SqlAlchemyUnitOfWork,
    ) -> None:
        self._planned = planned
        self._uow = uow

    def execute(self, data: CancelPlannedCashFlowInput) -> PlannedCashFlow:
        entity = self._planned.get_by_id(data.organization_id, data.cash_flow_id)
        if entity is None:
            raise PlannedCashFlowNotFoundError("Planned cash flow not found.")
        entity.cancel()
        saved = self._planned.save(entity)
        self._uow.commit()
        return saved
