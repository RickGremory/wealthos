"""Collect adapter contributions into an immutable PlanningContext."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import UTC, datetime

from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.domain.enums.alert import AlertSeverity
from wealthos.modules.planning.domain.enums.source import (
    SOURCE_COLLECTION_ORDER,
    PlanningSource,
    SourceStatus,
)
from wealthos.modules.planning.domain.exceptions import PlanningSourceUnavailable
from wealthos.modules.planning.domain.ports.source_adapter import (
    PlanningCollectionRequest,
    PlanningSourceAdapter,
    PlanningSourceContribution,
)
from wealthos.modules.planning.domain.value_objects.alerts import PlanningSourceSummary
from wealthos.modules.planning.domain.value_objects.collection_warning import (
    PlanningCollectionWarning,
    PlanningSourceMetadata,
)
from wealthos.modules.planning.domain.value_objects.projection_result import (
    PlanningContext,
    ProjectionPeriod,
)

logger = logging.getLogger(__name__)


class PlanningContextBuilder:
    """Stable order matters more than wall-clock concurrency for V1."""

    def __init__(self, adapters: Sequence[PlanningSourceAdapter]) -> None:
        by_name = {adapter.source_name: adapter for adapter in adapters}
        ordered: list[PlanningSourceAdapter] = []
        for source in SOURCE_COLLECTION_ORDER:
            adapter = by_name.pop(source.value, None)
            if adapter is not None:
                ordered.append(adapter)
        # Any extra adapters keep declaration order after the canonical set.
        ordered.extend(by_name.values())
        self._adapters = tuple(ordered)

    def build(
        self,
        *,
        period: ProjectionPeriod,
        settings: PlanningSettings,
        calculated_at: datetime,
        currency: str,
    ) -> PlanningContext:
        request = PlanningCollectionRequest(
            organization_id=settings.organization_id,
            currency=currency.strip().upper(),
            calculated_at=calculated_at,
            period_start=period.start,
            period_end=period.end,
            settings=settings,
            timezone=period.timezone,
        )

        accounts = []
        cash_flows = []
        reservations = []
        settlements = []
        warnings: list[PlanningCollectionWarning] = []
        sources: list[PlanningSourceSummary] = []

        for adapter in self._adapters:
            contribution = self._collect_one(adapter, request)
            accounts.extend(contribution.accounts)
            cash_flows.extend(contribution.cash_flows)
            reservations.extend(contribution.reservations)
            settlements.extend(contribution.settlements)
            warnings.extend(contribution.warnings)
            sources.append(self._to_summary(contribution, calculated_at))

        return PlanningContext(
            organization_id=settings.organization_id,
            currency=request.currency,
            calculated_at=calculated_at,
            period=period,
            settings=settings,
            accounts=tuple(accounts),
            cash_flows=tuple(cash_flows),
            reservations=tuple(reservations),
            settlements=tuple(settlements),
            sources=tuple(sources),
            warnings=tuple(warnings),
        )

    def _collect_one(
        self,
        adapter: PlanningSourceAdapter,
        request: PlanningCollectionRequest,
    ) -> PlanningSourceContribution:
        try:
            return adapter.collect(request)
        except PlanningSourceUnavailable as exc:
            now = datetime.now(UTC)
            return PlanningSourceContribution(
                source_name=adapter.source_name,
                warnings=(
                    PlanningCollectionWarning(
                        code="source_unavailable",
                        source_name=adapter.source_name,
                        message_key="planning.warning.source_unavailable",
                        severity=AlertSeverity.CRITICAL,
                    ),
                ),
                metadata=PlanningSourceMetadata(
                    source_name=adapter.source_name,
                    collected_at=now,
                    data_as_of=None,
                    status=SourceStatus.UNAVAILABLE,
                ),
            )
        except Exception:
            logger.exception(
                "planning.adapter.unexpected_failure",
                extra={"source_name": adapter.source_name},
            )
            now = datetime.now(UTC)
            return PlanningSourceContribution(
                source_name=adapter.source_name,
                warnings=(
                    PlanningCollectionWarning(
                        code="source_unavailable",
                        source_name=adapter.source_name,
                        message_key="planning.warning.source_failed",
                        severity=AlertSeverity.CRITICAL,
                    ),
                ),
                metadata=PlanningSourceMetadata(
                    source_name=adapter.source_name,
                    collected_at=now,
                    data_as_of=None,
                    status=SourceStatus.UNAVAILABLE,
                ),
            )

    @staticmethod
    def _to_summary(
        contribution: PlanningSourceContribution,
        calculated_at: datetime,
    ) -> PlanningSourceSummary:
        meta = contribution.metadata
        status = meta.status if meta else SourceStatus.AVAILABLE
        collected_at = meta.collected_at if meta else calculated_at
        data_as_of = meta.data_as_of if meta else None
        return PlanningSourceSummary(
            source_name=contribution.source_name,
            status=status,
            collected_at=collected_at,
            data_as_of=data_as_of,
            accounts=len(contribution.accounts),
            cash_flows=len(contribution.cash_flows),
            reservations=len(contribution.reservations),
            settlements=len(contribution.settlements),
            warnings=contribution.warnings,
        )


def default_adapter_order_names() -> tuple[str, ...]:
    return tuple(source.value for source in SOURCE_COLLECTION_ORDER)
