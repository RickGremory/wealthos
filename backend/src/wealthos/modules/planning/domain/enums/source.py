"""Planning sources, collection status and dedupe precedence (SPEC-004 §6)."""

from __future__ import annotations

from enum import StrEnum


class PlanningSource(StrEnum):
    ACCOUNTS = "accounts"
    TRANSACTIONS = "transactions"
    COMMITMENTS = "commitments"
    GOALS = "goals"
    TAXES = "taxes"
    RECURRING = "recurring"
    MANUAL_PLANNING = "manual_planning"


class SourceStatus(StrEnum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"


#: Stable collection order. Accounts first because liquidity is critical.
SOURCE_COLLECTION_ORDER: tuple[PlanningSource, ...] = (
    PlanningSource.ACCOUNTS,
    PlanningSource.TRANSACTIONS,
    PlanningSource.COMMITMENTS,
    PlanningSource.GOALS,
    PlanningSource.TAXES,
    PlanningSource.RECURRING,
    PlanningSource.MANUAL_PLANNING,
)

#: When two sources claim the same ``occurrence_key``, the higher score wins.
SOURCE_PRECEDENCE: dict[str, int] = {
    PlanningSource.COMMITMENTS.value: 100,
    PlanningSource.TAXES.value: 90,
    PlanningSource.GOALS.value: 80,
    PlanningSource.MANUAL_PLANNING.value: 70,
    PlanningSource.RECURRING.value: 60,
    PlanningSource.TRANSACTIONS.value: 10,
    PlanningSource.ACCOUNTS.value: 0,
}


def source_precedence(source_name: str) -> int:
    return SOURCE_PRECEDENCE.get(source_name.strip().lower(), 0)
