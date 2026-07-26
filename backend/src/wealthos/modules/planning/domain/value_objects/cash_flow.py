"""Immutable cash flow DTO the projection engine consumes."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import datetime
from decimal import Decimal
from types import MappingProxyType
from uuid import UUID

from wealthos.modules.planning.domain.enums.cash_flow import (
    CashFlowCertainty,
    CashFlowDirection,
    CashFlowStatus,
)
from wealthos.modules.planning.domain.value_objects.money_utils import ZERO
from wealthos.modules.planning.domain.value_objects.source_reference import (
    PlanningSourceReference,
)

_EMPTY_METADATA: Mapping[str, object] = MappingProxyType({})


@dataclass(frozen=True, slots=True)
class PlanningCashFlow:
    """A dated future movement.

    The engine always works on ``outstanding_amount`` — the part that still
    moves money — never on the original ``amount``.
    """

    id: str
    organization_id: UUID
    direction: CashFlowDirection
    amount: Decimal
    outstanding_amount: Decimal
    currency: str
    expected_at: datetime
    certainty: CashFlowCertainty
    status: CashFlowStatus
    category: str
    label: str
    source: PlanningSourceReference
    metadata: Mapping[str, object] = field(default=_EMPTY_METADATA)

    @property
    def occurrence_key(self) -> str:
        return self.source.occurrence_key

    @property
    def source_name(self) -> str:
        return self.source.source_name

    @property
    def signed_outstanding(self) -> Decimal:
        return (
            self.outstanding_amount
            if self.direction is CashFlowDirection.INFLOW
            else -self.outstanding_amount
        )

    @property
    def is_open(self) -> bool:
        return self.status.affects_projection and self.outstanding_amount > ZERO

    def with_outstanding(
        self,
        outstanding_amount: Decimal,
        *,
        status: CashFlowStatus | None = None,
    ) -> PlanningCashFlow:
        return replace(
            self,
            outstanding_amount=outstanding_amount,
            status=status or self.status,
        )
