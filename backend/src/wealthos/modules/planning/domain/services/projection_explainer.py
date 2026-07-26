"""Turn the projection into a narrative chain (§24: always explain)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from wealthos.modules.planning.domain.policies.safe_to_spend import SafeToSpendOutcome
from wealthos.modules.planning.domain.value_objects.alerts import (
    PlanningExplanation,
    PlanningExplanationStep,
)
from wealthos.modules.planning.domain.value_objects.money_utils import ZERO
from wealthos.modules.planning.domain.value_objects.projection_point import ProjectionPoint


class PlanningProjectionExplainer:
    """Names the binding constraint so the number is never opaque."""

    def explain(
        self,
        *,
        timeline: tuple[ProjectionPoint, ...],
        required_reserve: Decimal,
        minimum_balance: Decimal | None,
        minimum_balance_at: datetime | None,
        outcome: SafeToSpendOutcome | None,
    ) -> PlanningExplanation:
        steps = tuple(
            PlanningExplanationStep(
                key="opening_cash" if point.is_opening else "cash_flow",
                label=point.label,
                amount=point.delta,
                running_balance=point.balance,
            )
            for point in timeline
        )

        if outcome is None:
            return PlanningExplanation(
                steps=steps,
                required_reserve=required_reserve,
                minimum_balance=minimum_balance,
                minimum_balance_at=minimum_balance_at,
                safe_to_spend=None,
                binding_constraint="not_computable",
            )

        steps = (
            *steps,
            PlanningExplanationStep(
                key="required_reserve",
                label="planning.explanation.required_reserve",
                amount=-required_reserve,
                running_balance=None,
            ),
            PlanningExplanationStep(
                key="safe_to_spend",
                label="planning.explanation.safe_to_spend",
                amount=outcome.safe_to_spend,
                running_balance=None,
            ),
        )

        return PlanningExplanation(
            steps=steps,
            required_reserve=required_reserve,
            minimum_balance=minimum_balance,
            minimum_balance_at=minimum_balance_at,
            safe_to_spend=outcome.safe_to_spend,
            binding_constraint=self._binding_constraint(outcome, required_reserve),
        )

    def _binding_constraint(
        self,
        outcome: SafeToSpendOutcome,
        required_reserve: Decimal,
    ) -> str:
        if outcome.cash_deficit is not None:
            return "cash_deficit"
        if outcome.reserve_shortfall is not None:
            return "reserve"
        if outcome.safe_to_spend <= ZERO and required_reserve > ZERO:
            return "reserve"
        return "none"
