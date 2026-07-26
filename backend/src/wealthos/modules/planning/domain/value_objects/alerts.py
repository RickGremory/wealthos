"""Explanation surface: alerts, exclusions, breakdown, per-source summary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from wealthos.modules.planning.domain.enums.alert import AlertSeverity
from wealthos.modules.planning.domain.enums.cash_flow import CashFlowCertainty
from wealthos.modules.planning.domain.enums.source import SourceStatus
from wealthos.modules.planning.domain.value_objects.collection_warning import (
    PlanningCollectionWarning,
)


@dataclass(frozen=True, slots=True)
class PlanningAlert:
    code: str
    severity: AlertSeverity
    message_key: str
    related_resource_type: str | None = None
    related_resource_id: str | None = None
    date: datetime | None = None
    amount: Decimal | None = None
    currency: str | None = None


@dataclass(frozen=True, slots=True)
class ExcludedPlanningItem:
    """Every item kept out of the math must be explainable."""

    occurrence_key: str
    label: str
    reason_code: str
    amount: Decimal
    currency: str
    date: datetime | None
    source_name: str


@dataclass(frozen=True, slots=True)
class PlanningBreakdownItem:
    id: str
    category: str
    label: str
    amount: Decimal
    currency: str
    date: datetime | None
    direction: str  # "add" | "subtract"
    source_name: str
    source_id: str | None
    certainty: CashFlowCertainty | None
    included: bool
    exclusion_reason: str | None = None


@dataclass(frozen=True, slots=True)
class PlanningSourceSummary:
    """Diagnostic view behind ``GET …/planning/sources``."""

    source_name: str
    status: SourceStatus
    collected_at: datetime
    data_as_of: datetime | None
    accounts: int = 0
    cash_flows: int = 0
    reservations: int = 0
    settlements: int = 0
    warnings: tuple[PlanningCollectionWarning, ...] = ()


@dataclass(frozen=True, slots=True)
class PlanningExplanationStep:
    key: str
    label: str
    amount: Decimal | None
    running_balance: Decimal | None


@dataclass(frozen=True, slots=True)
class PlanningExplanation:
    """Narrative chain — "según la información registrada", never absolutes."""

    steps: tuple[PlanningExplanationStep, ...]
    required_reserve: Decimal
    minimum_balance: Decimal | None
    minimum_balance_at: datetime | None
    safe_to_spend: Decimal | None
    binding_constraint: str  # "none" | "reserve" | "cash_deficit" | "not_computable"
