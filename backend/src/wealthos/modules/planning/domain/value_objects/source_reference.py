"""Cross-cutting identity for every projected occurrence (SPEC-004 §6)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanningSourceReference:
    """Stable identity so the same obligation collapses to one effect.

    ``occurrence_key`` examples::

        commitment:{id}:due:2026-08-15
        recurring:{id}:occurrence:2026-08-20
        goal:{id}:contribution:2026-08
        tax:{id}:period:2026-07:payment
        planned:{id}
    """

    source_name: str
    resource_type: str
    resource_id: str
    occurrence_key: str
    resource_version: int | None = None
