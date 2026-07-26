"""Commitment calendar event response schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from wealthos.modules.debts.application.queries.get_commitment_calendar import (
    CommitmentCalendarResult,
)


class CommitmentCalendarEventResponse(BaseModel):
    id: str
    commitment_id: UUID
    name: str
    event_type: str
    event_date: date
    severity: str
    currency: str
    amount: Decimal | None = None


class CommitmentCalendarResponse(BaseModel):
    items: list[CommitmentCalendarEventResponse] = Field(default_factory=list)
    total: int = 0

    @classmethod
    def from_result(cls, result: CommitmentCalendarResult) -> CommitmentCalendarResponse:
        items = [
            CommitmentCalendarEventResponse(
                id=item.id,
                commitment_id=item.commitment_id,
                name=item.name,
                event_type=item.event_type,
                event_date=item.event_date,
                severity=item.severity,
                currency=item.currency,
                amount=item.amount,
            )
            for item in result.items
        ]
        return cls(items=items, total=len(items))
