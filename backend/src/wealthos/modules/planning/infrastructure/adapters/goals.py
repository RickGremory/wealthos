"""Goals → reservations (protected / emergency fund outstanding)."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from wealthos.modules.goals.application.services.goal_progress_service import (
    GoalProgressService,
)
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.modules.planning.domain.enums.reservation import ReservationType
from wealthos.modules.planning.domain.enums.source import PlanningSource, SourceStatus
from wealthos.modules.planning.domain.ports.source_adapter import (
    PlanningCollectionRequest,
    PlanningSourceContribution,
)
from wealthos.modules.planning.domain.value_objects.collection_warning import (
    PlanningSourceMetadata,
)
from wealthos.modules.planning.domain.value_objects.money_utils import quantize_money
from wealthos.modules.planning.domain.value_objects.reservation import PlanningReservation
from wealthos.modules.planning.domain.value_objects.source_reference import (
    PlanningSourceReference,
)


class GoalsPlanningAdapter:
    source_name = PlanningSource.GOALS.value

    def __init__(
        self,
        goals: GoalRepository,
        progress: GoalProgressService | None = None,
    ) -> None:
        self._goals = goals
        self._progress = progress or GoalProgressService(goals)

    def collect(self, request: PlanningCollectionRequest) -> PlanningSourceContribution:
        now = datetime.now(UTC)
        currency = request.currency.strip().upper()
        reservations: list[PlanningReservation] = []

        for goal in self._goals.list_by_organization(
            request.organization_id,
            include_archived=False,
        ):
            if goal.target_amount.currency.value != currency:
                continue
            if not goal.status.is_active:
                continue

            progress = self._progress.calculate(goal)
            remaining = quantize_money(progress.remaining_amount.amount)
            current = quantize_money(progress.current_amount.amount)
            if remaining <= Decimal("0") and current <= Decimal("0"):
                continue

            key = f"goal:{goal.id}:protected"
            reservations.append(
                PlanningReservation(
                    id=key,
                    organization_id=request.organization_id,
                    reservation_type=ReservationType.GOAL,
                    label=str(goal.name),
                    required_amount=quantize_money(goal.target_amount.amount),
                    already_protected_amount=current,
                    outstanding_amount=remaining,
                    currency=currency,
                    effective_at=None,
                    source=PlanningSourceReference(
                        source_name=self.source_name,
                        resource_type="goal",
                        resource_id=str(goal.id),
                        occurrence_key=key,
                    ),
                )
            )

        return PlanningSourceContribution(
            source_name=self.source_name,
            reservations=tuple(reservations),
            metadata=PlanningSourceMetadata(
                source_name=self.source_name,
                collected_at=now,
                data_as_of=now,
                status=SourceStatus.AVAILABLE,
            ),
        )
