"""Planning projection enums (SPEC-004)."""

from .alert import AlertSeverity, PlanningAlertCode, PlanningExclusionReason
from .cash_flow import CashFlowCertainty, CashFlowDirection, CashFlowStatus
from .planning_horizon import PlanningHorizon
from .projection import ProjectionConfidence, ProjectionStatus
from .reservation import ReservationType, SafetyReserveStrategy
from .scenario import ScenarioAdjustmentType, scenario_occurrence_key
from .source import (
    SOURCE_COLLECTION_ORDER,
    SOURCE_PRECEDENCE,
    PlanningSource,
    SourceStatus,
    source_precedence,
)

__all__ = [
    "SOURCE_COLLECTION_ORDER",
    "SOURCE_PRECEDENCE",
    "AlertSeverity",
    "CashFlowCertainty",
    "CashFlowDirection",
    "CashFlowStatus",
    "PlanningAlertCode",
    "PlanningExclusionReason",
    "PlanningHorizon",
    "PlanningSource",
    "ProjectionConfidence",
    "ProjectionStatus",
    "ReservationType",
    "SafetyReserveStrategy",
    "ScenarioAdjustmentType",
    "SourceStatus",
    "scenario_occurrence_key",
    "source_precedence",
]
