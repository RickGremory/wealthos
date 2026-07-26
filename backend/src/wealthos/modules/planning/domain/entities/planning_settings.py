"""PlanningSettings — the only org-level configuration Planning persists."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.planning.domain.enums.planning_horizon import PlanningHorizon
from wealthos.modules.planning.domain.enums.reservation import SafetyReserveStrategy
from wealthos.modules.planning.domain.exceptions import (
    InvalidSafetyReserveAmount,
    LinkedEmergencyGoalRequired,
)
from wealthos.modules.planning.domain.value_objects.money_utils import quantize_money

DEFAULT_HORIZON = PlanningHorizon.THIRTY_DAYS
DEFAULT_RESERVE_STRATEGY = SafetyReserveStrategy.NONE
DEFAULT_INCLUDE_EXPECTED_INCOME = True
DEFAULT_INCLUDE_ESTIMATED_EXPENSES = True


@dataclass(slots=True)
class PlanningSettings:
    id: UUID
    organization_id: UUID
    default_horizon: PlanningHorizon
    safety_reserve_strategy: SafetyReserveStrategy
    safety_reserve_amount: Decimal | None
    linked_emergency_goal_id: UUID | None
    include_expected_income: bool
    include_estimated_expenses: bool
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        default_horizon: str | PlanningHorizon = DEFAULT_HORIZON,
        safety_reserve_strategy: str | SafetyReserveStrategy = DEFAULT_RESERVE_STRATEGY,
        safety_reserve_amount: Decimal | str | int | None = None,
        linked_emergency_goal_id: UUID | None = None,
        include_expected_income: bool = DEFAULT_INCLUDE_EXPECTED_INCOME,
        include_estimated_expenses: bool = DEFAULT_INCLUDE_ESTIMATED_EXPENSES,
        settings_id: UUID | None = None,
    ) -> PlanningSettings:
        strategy = SafetyReserveStrategy.parse(safety_reserve_strategy)
        amount = _normalize_reserve_amount(safety_reserve_amount)
        _validate_strategy(strategy, amount, linked_emergency_goal_id)

        now = datetime.now(UTC)
        return cls(
            id=settings_id or uuid4(),
            organization_id=organization_id,
            default_horizon=PlanningHorizon.parse(default_horizon),
            safety_reserve_strategy=strategy,
            safety_reserve_amount=amount,
            linked_emergency_goal_id=linked_emergency_goal_id,
            include_expected_income=include_expected_income,
            include_estimated_expenses=include_estimated_expenses,
            version=1,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def defaults(cls, organization_id: UUID) -> PlanningSettings:
        """In-memory defaults for orgs that never opened Planning settings."""
        return cls.create(organization_id=organization_id)

    def update(
        self,
        *,
        default_horizon: str | PlanningHorizon | None = None,
        safety_reserve_strategy: str | SafetyReserveStrategy | None = None,
        safety_reserve_amount: Decimal | str | int | None = None,
        linked_emergency_goal_id: UUID | None = None,
        include_expected_income: bool | None = None,
        include_estimated_expenses: bool | None = None,
        fields_set: frozenset[str] | None = None,
    ) -> None:
        touched = fields_set

        def is_set(field: str) -> bool:
            return touched is None or field in touched

        if default_horizon is not None and is_set("default_horizon"):
            self.default_horizon = PlanningHorizon.parse(default_horizon)

        strategy = self.safety_reserve_strategy
        if safety_reserve_strategy is not None and is_set("safety_reserve_strategy"):
            strategy = SafetyReserveStrategy.parse(safety_reserve_strategy)

        amount = self.safety_reserve_amount
        if is_set("safety_reserve_amount"):
            amount = _normalize_reserve_amount(safety_reserve_amount)

        goal_id = self.linked_emergency_goal_id
        if is_set("linked_emergency_goal_id"):
            goal_id = linked_emergency_goal_id

        _validate_strategy(strategy, amount, goal_id)
        self.safety_reserve_strategy = strategy
        self.safety_reserve_amount = amount
        self.linked_emergency_goal_id = goal_id

        if include_expected_income is not None and is_set("include_expected_income"):
            self.include_expected_income = include_expected_income
        if include_estimated_expenses is not None and is_set("include_estimated_expenses"):
            self.include_estimated_expenses = include_estimated_expenses

        self.bump_version()

    def bump_version(self) -> None:
        self.updated_at = datetime.now(UTC)
        self.version += 1


def _normalize_reserve_amount(value: Decimal | str | int | None) -> Decimal | None:
    if value is None:
        return None
    amount = quantize_money(value)
    if amount < Decimal("0.00"):
        raise InvalidSafetyReserveAmount("Safety reserve amount cannot be negative.")
    return amount


def _validate_strategy(
    strategy: SafetyReserveStrategy,
    amount: Decimal | None,
    linked_emergency_goal_id: UUID | None,
) -> None:
    if strategy is SafetyReserveStrategy.FIXED_AMOUNT and amount is None:
        raise InvalidSafetyReserveAmount("fixed_amount strategy requires a reserve amount.")
    if strategy is SafetyReserveStrategy.LINKED_GOAL and linked_emergency_goal_id is None:
        raise LinkedEmergencyGoalRequired("linked_goal strategy requires an emergency goal.")
