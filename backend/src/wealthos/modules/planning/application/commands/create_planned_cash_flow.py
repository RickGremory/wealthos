"""Create a manual planned cash flow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from wealthos.modules.planning.domain.entities.planned_cash_flow import PlannedCashFlow
from wealthos.modules.planning.domain.ports.repositories import PlannedCashFlowRepository
from wealthos.shared.domain.value_objects.money import Money
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


@dataclass(frozen=True, slots=True)
class CreatePlannedCashFlowInput:
    organization_id: UUID
    name: str
    direction: str
    amount: Decimal
    currency: str
    expected_at: datetime
    certainty: str
    notes: str | None = None


class CreatePlannedCashFlowCommand:
    def __init__(
        self,
        planned: PlannedCashFlowRepository,
        uow: SqlAlchemyUnitOfWork,
    ) -> None:
        self._planned = planned
        self._uow = uow

    def execute(self, data: CreatePlannedCashFlowInput) -> PlannedCashFlow:
        entity = PlannedCashFlow.create(
            organization_id=data.organization_id,
            name=data.name,
            direction=data.direction,
            amount=Money(data.amount, data.currency),
            expected_at=data.expected_at,
            certainty=data.certainty,
            notes=data.notes,
        )
        saved = self._planned.add(entity)
        self._uow.commit()
        return saved
