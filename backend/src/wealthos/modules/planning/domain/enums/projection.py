"""Projection status and confidence labels (SPEC-004 §5, §6)."""

from __future__ import annotations

from enum import StrEnum


class ProjectionStatus(StrEnum):
    HEALTHY = "healthy"
    LIMITED = "limited"
    ZERO = "zero"
    DEFICIT = "deficit"
    INSUFFICIENT_DATA = "insufficient_data"
    UNAVAILABLE = "unavailable"

    @property
    def is_computable(self) -> bool:
        """``safe_to_spend`` is ``null`` — not zero — for non-computable states."""
        return self not in {
            ProjectionStatus.INSUFFICIENT_DATA,
            ProjectionStatus.UNAVAILABLE,
        }


class ProjectionConfidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
