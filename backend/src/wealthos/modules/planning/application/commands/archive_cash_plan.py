"""ArchiveCashPlan command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.planning.domain.entities.cash_plan import CashPlan
from wealthos.modules.planning.domain.exceptions import CashPlanNotFoundError
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)


@dataclass(frozen=True, slots=True)
class ArchiveCashPlanInput:
    organization_id: UUID
    cash_plan_id: UUID


class ArchiveCashPlanCommand:
    def __init__(self, cash_plans: CashPlanRepository) -> None:
        self._cash_plans = cash_plans

    def execute(self, data: ArchiveCashPlanInput) -> CashPlan:
        plan = self._cash_plans.get_by_id(data.organization_id, data.cash_plan_id)
        if plan is None:
            raise CashPlanNotFoundError("Cash plan not found.")
        plan.archive()
        return self._cash_plans.save(plan)
