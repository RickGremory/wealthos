"""List planned cash flows for an organization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from wealthos.modules.planning.domain.entities.planned_cash_flow import PlannedCashFlow
from wealthos.modules.planning.domain.ports.repositories import PlannedCashFlowRepository


@dataclass(frozen=True, slots=True)
class ListPlannedCashFlowsInput:
    organization_id: UUID
    currency: str | None = None
    status: str | None = None
    direction: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = 200
    offset: int = 0


class ListPlannedCashFlowsQuery:
    def __init__(self, planned: PlannedCashFlowRepository) -> None:
        self._planned = planned

    def execute(self, data: ListPlannedCashFlowsInput) -> list[PlannedCashFlow]:
        return self._planned.list_by_organization(
            data.organization_id,
            currency=data.currency,
            status=data.status,
            direction=data.direction,
            date_from=data.date_from,
            date_to=data.date_to,
            limit=data.limit,
            offset=data.offset,
        )
