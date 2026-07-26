"""Taxes → partial contribution until a full tax engine feeds Planning."""

from __future__ import annotations

from datetime import UTC, datetime

from wealthos.modules.planning.domain.enums.alert import AlertSeverity
from wealthos.modules.planning.domain.enums.source import PlanningSource, SourceStatus
from wealthos.modules.planning.domain.ports.source_adapter import (
    PlanningCollectionRequest,
    PlanningSourceContribution,
)
from wealthos.modules.planning.domain.value_objects.collection_warning import (
    PlanningCollectionWarning,
    PlanningSourceMetadata,
)


class TaxesPlanningAdapter:
    """V1: do not invent ISR/IVA. Mark partial until reserves exist."""

    source_name = PlanningSource.TAXES.value

    def collect(self, request: PlanningCollectionRequest) -> PlanningSourceContribution:
        now = datetime.now(UTC)
        return PlanningSourceContribution(
            source_name=self.source_name,
            warnings=(
                PlanningCollectionWarning(
                    code="tax_reservation_incomplete",
                    source_name=self.source_name,
                    message_key="planning.warning.tax_partial",
                    severity=AlertSeverity.INFO,
                ),
            ),
            metadata=PlanningSourceMetadata(
                source_name=self.source_name,
                collected_at=now,
                data_as_of=None,
                status=SourceStatus.PARTIAL,
            ),
        )
