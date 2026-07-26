"""Context builder stable order and adapter failure handling."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.domain.enums.planning_horizon import PlanningHorizon
from wealthos.modules.planning.domain.enums.source import (
    SOURCE_COLLECTION_ORDER,
    SourceStatus,
)
from wealthos.modules.planning.domain.exceptions import PlanningSourceUnavailable
from wealthos.modules.planning.domain.ports.source_adapter import (
    PlanningCollectionRequest,
    PlanningSourceContribution,
)
from wealthos.modules.planning.domain.services.context_builder import PlanningContextBuilder
from wealthos.modules.planning.domain.services.horizon_resolver import (
    PlanningHorizonResolver,
)
from wealthos.modules.planning.domain.value_objects.collection_warning import (
    PlanningSourceMetadata,
)


class _StubAdapter:
    def __init__(self, name: str, *, fail: bool = False) -> None:
        self.source_name = name
        self._fail = fail

    def collect(self, request: PlanningCollectionRequest) -> PlanningSourceContribution:
        if self._fail:
            raise PlanningSourceUnavailable(self.source_name)
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


def test_context_builder_preserves_stable_source_order() -> None:
    adapters = [_StubAdapter(name.value) for name in reversed(SOURCE_COLLECTION_ORDER)]
    builder = PlanningContextBuilder(adapters)
    settings = PlanningSettings.defaults(uuid4())
    period = PlanningHorizonResolver().resolve(
        horizon=PlanningHorizon.THIRTY_DAYS,
        timezone="UTC",
        calculated_at=datetime(2026, 8, 1, tzinfo=UTC),
    )
    context = builder.build(
        period=period,
        settings=settings,
        calculated_at=period.start,
        currency="MXN",
    )
    assert [s.source_name for s in context.sources] == [
        name.value for name in SOURCE_COLLECTION_ORDER
    ]


def test_context_builder_marks_unavailable_source() -> None:
    builder = PlanningContextBuilder([_StubAdapter("accounts", fail=True)])
    settings = PlanningSettings.defaults(uuid4())
    period = PlanningHorizonResolver().resolve(
        horizon=PlanningHorizon.THIRTY_DAYS,
        timezone="UTC",
        calculated_at=datetime(2026, 8, 1, tzinfo=UTC),
    )
    context = builder.build(
        period=period,
        settings=settings,
        calculated_at=period.start,
        currency="MXN",
    )
    assert context.sources[0].status is SourceStatus.UNAVAILABLE
    assert context.warnings
