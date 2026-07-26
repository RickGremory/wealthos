"""Scenario adjustment kinds (SPEC-004 §7)."""

from __future__ import annotations

from enum import StrEnum

SCENARIO_KEY_PREFIX = "scenario"


class ScenarioAdjustmentType(StrEnum):
    ADD_CASH_FLOW = "add_cash_flow"
    REMOVE_CASH_FLOW = "remove_cash_flow"
    CHANGE_RESERVE = "change_reserve"


def scenario_occurrence_key(adjustment_id: str) -> str:
    """Temporary identity so simulated flows never collide with real ones."""
    return f"{SCENARIO_KEY_PREFIX}:{adjustment_id}"
