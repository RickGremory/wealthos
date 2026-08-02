"""Canonical FinancialEvent contract for Timeline projection."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID, uuid4

SourceType = Literal[
    "transaction",
    "goal",
    "commitment",
    "planning",
    "tax",
    "system",
    "recurring",
]
Importance = Literal["low", "normal", "high", "critical"]


@dataclass(frozen=True, slots=True)
class FinancialEvent:
    organization_id: UUID
    occurred_at: datetime
    source_type: SourceType
    event_type: str
    importance: Importance
    title: str
    description: str
    resource_type: str
    resource_id: UUID
    id: UUID = field(default_factory=uuid4)
    currency: str | None = None
    amount: Decimal | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
