"""Adapter protocol: each source emits only what it owns (SPEC-004 §4)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.domain.value_objects.account_snapshot import (
    PlanningAccountSnapshot,
)
from wealthos.modules.planning.domain.value_objects.cash_flow import PlanningCashFlow
from wealthos.modules.planning.domain.value_objects.collection_warning import (
    PlanningCollectionWarning,
    PlanningSourceMetadata,
)
from wealthos.modules.planning.domain.value_objects.reservation import PlanningReservation
from wealthos.modules.planning.domain.value_objects.settlement import PlanningSettlement


@dataclass(frozen=True, slots=True)
class PlanningCollectionRequest:
    organization_id: UUID
    currency: str
    calculated_at: datetime
    period_start: datetime
    period_end: datetime
    settings: PlanningSettings
    timezone: str = "UTC"


@dataclass(frozen=True, slots=True)
class PlanningSourceContribution:
    source_name: str
    accounts: tuple[PlanningAccountSnapshot, ...] = ()
    cash_flows: tuple[PlanningCashFlow, ...] = ()
    reservations: tuple[PlanningReservation, ...] = ()
    settlements: tuple[PlanningSettlement, ...] = ()
    warnings: tuple[PlanningCollectionWarning, ...] = ()
    metadata: PlanningSourceMetadata | None = None


class PlanningSourceAdapter(Protocol):
    """Owning modules implement this; Planning depends only on the port."""

    @property
    def source_name(self) -> str: ...

    def collect(self, request: PlanningCollectionRequest) -> PlanningSourceContribution: ...
