"""Money that exists but must not count as spendable."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from types import MappingProxyType
from uuid import UUID

from wealthos.modules.planning.domain.enums.reservation import (
    ReservationType,
    SafetyReserveStrategy,
)
from wealthos.modules.planning.domain.value_objects.source_reference import (
    PlanningSourceReference,
)

_EMPTY_METADATA: Mapping[str, object] = MappingProxyType({})


@dataclass(frozen=True, slots=True)
class PlanningReservation:
    """Not always a future outflow — an emergency fund reserves without a date."""

    id: str
    organization_id: UUID
    reservation_type: ReservationType
    label: str
    required_amount: Decimal
    already_protected_amount: Decimal
    outstanding_amount: Decimal
    currency: str
    effective_at: datetime | None
    source: PlanningSourceReference
    metadata: Mapping[str, object] = field(default=_EMPTY_METADATA)

    @property
    def occurrence_key(self) -> str:
        return self.source.occurrence_key


@dataclass(frozen=True, slots=True)
class SafetyReserveResult:
    """Resolved minimum balance the projection must never breach."""

    strategy: SafetyReserveStrategy
    required_amount: Decimal
    label: str
    reason_codes: tuple[str, ...] = ()
    source_reservation_key: str | None = None
