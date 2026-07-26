"""Alert severities and the V1 planning alert vocabulary (SPEC-004 §33–34)."""

from __future__ import annotations

from enum import StrEnum


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class PlanningAlertCode(StrEnum):
    PROJECTED_DEFICIT = "projected_deficit"
    SAFETY_RESERVE_NOT_CONFIGURED = "safety_reserve_not_configured"
    SAFETY_RESERVE_STRATEGY_UNSUPPORTED = "safety_reserve_strategy_unsupported"
    SAFETY_RESERVE_GOAL_UNAVAILABLE = "safety_reserve_goal_unavailable"
    LOW_PROJECTION_CONFIDENCE = "low_projection_confidence"
    MISSING_EXPECTED_INCOME_DATE = "missing_expected_income_date"
    MISSING_COMMITMENT_PAYMENT = "missing_commitment_payment"
    DUPLICATE_CASH_FLOW_EXCLUDED = "duplicate_cash_flow_excluded"
    POSSIBLE_DUPLICATE_CASH_FLOW = "possible_duplicate_cash_flow"
    STALE_ACCOUNT_BALANCE = "stale_account_balance"
    GOAL_ALLOCATION_AT_RISK = "goal_allocation_at_risk"
    TAX_RESERVATION_INCOMPLETE = "tax_reservation_incomplete"
    NO_ELIGIBLE_ACCOUNTS = "no_eligible_accounts"
    SOURCE_UNAVAILABLE = "source_unavailable"
    SOURCE_PARTIAL = "source_partial"
    RESERVE_SHORTFALL = "reserve_shortfall"


class PlanningExclusionReason(StrEnum):
    ESTIMATED_INCOME_EXCLUDED = "estimated_income_excluded"
    EXPECTED_INCOME_DISABLED = "expected_income_disabled"
    ESTIMATED_EXPENSES_DISABLED = "estimated_expenses_disabled"
    ALREADY_SETTLED = "already_settled"
    CANCELLED = "cancelled"
    OUTSIDE_HORIZON = "outside_horizon"
    DUPLICATE_OCCURRENCE = "duplicate_occurrence"
    CURRENCY_MISMATCH = "currency_mismatch"
    NON_LIQUID_ACCOUNT = "non_liquid_account"
    ARCHIVED_ACCOUNT = "archived_account"
