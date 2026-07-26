"""Posted facts that satisfy projected occurrences (anti double-count)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class PlanningSettlement:
    """Evidence a projected occurrence already happened.

    V1 reconciles on ``source_occurrence_key`` only; heuristic matching by
    amount/date raises a warning instead of consuming an occurrence.
    """

    transaction_id: UUID
    organization_id: UUID
    amount: Decimal
    currency: str
    settled_at: datetime
    source_occurrence_key: str | None
    related_resource_type: str | None = None
    related_resource_id: str | None = None
