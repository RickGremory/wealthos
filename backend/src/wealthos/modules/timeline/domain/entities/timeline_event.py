"""Timeline event entity (projection row)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class TimelineEvent:
    id: UUID
    organization_id: UUID
    occurred_at: datetime
    source_type: str
    event_type: str
    importance: str
    title: str
    description: str
    resource_type: str
    resource_id: UUID
    currency: str | None
    amount: Decimal | None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
