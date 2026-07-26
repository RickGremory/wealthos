"""Recurring stub until Sprint 9 expands occurrences."""

from __future__ import annotations

from datetime import UTC, datetime

from wealthos.modules.planning.domain.enums.source import PlanningSource, SourceStatus
from wealthos.modules.planning.domain.ports.source_adapter import (
    PlanningCollectionRequest,
    PlanningSourceContribution,
)
from wealthos.modules.planning.domain.value_objects.collection_warning import (
    PlanningSourceMetadata,
)


class RecurringPlanningAdapter:
    """Empty but available — Planning must not block on Recurring."""

    source_name = PlanningSource.RECURRING.value

    def collect(self, request: PlanningCollectionRequest) -> PlanningSourceContribution:
        now = datetime.now(UTC)
        return PlanningSourceContribution(
            source_name=self.source_name,
            metadata=PlanningSourceMetadata(
                source_name=self.source_name,
                collected_at=now,
                data_as_of=now,
                status=SourceStatus.AVAILABLE,
            ),
        )
