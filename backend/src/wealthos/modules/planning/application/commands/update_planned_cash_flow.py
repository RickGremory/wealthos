"""Update a manual planned cash flow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from wealthos.modules.planning.domain.entities.planned_cash_flow import PlannedCashFlow
from wealthos.modules.planning.domain.exceptions import (
    PlannedCashFlowNotFoundError,
    PlanningVersionConflict,
)
from wealthos.modules.planning.domain.ports.repositories import PlannedCashFlowRepository
from wealthos.shared.domain.value_objects.money import Money
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


@dataclass(frozen=True, slots=True)
class UpdatePlannedCashFlowInput:
    organization_id: UUID
    cash_flow_id: UUID
    expected_version: int
    name: str | None = None
    direction: str | None = None
    amount: Decimal | None = None
    expected_at: datetime | None = None
    certainty: str | None = None
    notes: str | None = None
    fields_set: frozenset[str] = frozenset()


class UpdatePlannedCashFlowCommand:
    def __init__(
        self,
        planned: PlannedCashFlowRepository,
        uow: SqlAlchemyUnitOfWork,
    ) -> None:
        self._planned = planned
        self._uow = uow

    def execute(self, data: UpdatePlannedCashFlowInput) -> PlannedCashFlow:
        entity = self._planned.get_by_id(data.organization_id, data.cash_flow_id)
        if entity is None:
            raise PlannedCashFlowNotFoundError("Planned cash flow not found.")
        if entity.version != data.expected_version:
            raise PlanningVersionConflict("Planned cash flow was modified by another request.")

        amount = None
        if "amount" in data.fields_set and data.amount is not None:
            amount = Money(data.amount, entity.amount.currency.value)

        entity.update(
            name=data.name,
            direction=data.direction,
            amount=amount,
            expected_at=data.expected_at,
            certainty=data.certainty,
            notes=data.notes,
            fields_set=data.fields_set,
        )
        saved = self._planned.save(entity)
        self._uow.commit()
        return saved
