"""One step of the chronological balance projection."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from wealthos.modules.planning.domain.enums.cash_flow import (
    CashFlowCertainty,
    CashFlowDirection,
)


@dataclass(frozen=True, slots=True)
class ProjectionPoint:
    """``t0`` (opening cash) plus one point per included event."""

    at: datetime
    label: str
    delta: Decimal
    balance: Decimal
    flow_id: str | None = None
    occurrence_key: str | None = None
    direction: CashFlowDirection | None = None
    certainty: CashFlowCertainty | None = None
    category: str = "current_cash"
    source_name: str | None = None

    @property
    def is_opening(self) -> bool:
        return self.flow_id is None
