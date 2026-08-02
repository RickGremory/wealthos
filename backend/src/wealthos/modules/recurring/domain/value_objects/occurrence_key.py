"""Stable occurrence identity for Recurring."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OccurrenceKey:
    value: str

    @classmethod
    def for_recurring_rule(cls, rule_id: UUID, original_date: date) -> OccurrenceKey:
        return cls(f"recurring:{rule_id}:occurrence:{original_date.isoformat()}")

    def __str__(self) -> str:
        return self.value
