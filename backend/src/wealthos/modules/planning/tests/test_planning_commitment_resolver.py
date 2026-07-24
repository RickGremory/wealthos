"""PlanningCommitmentResolver priority and dedupe tests."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from wealthos.modules.planning.application.services.planning_commitment_resolver import (
    PlanningCommitment,
    PlanningCommitmentResolver,
)


def test_keeps_highest_priority_for_same_debt() -> None:
    debt_id = uuid4()
    matched = PlanningCommitment(
        source="matched_transaction",
        amount=Decimal("1500.00"),
        expected_date=date(2026, 8, 20),
        debt_id=debt_id,
    )
    confirmed = PlanningCommitment(
        source="confirmed_cash_plan_item",
        amount=Decimal("1500.00"),
        expected_date=date(2026, 8, 25),
        debt_id=debt_id,
    )
    recommendation = PlanningCommitment(
        source="linked_module_recommendation",
        amount=Decimal("1500.00"),
        expected_date=date(2026, 8, 25),
        debt_id=debt_id,
    )
    budget = PlanningCommitment(
        source="budget_allocation",
        amount=Decimal("1500.00"),
        debt_id=debt_id,
    )

    resolved = PlanningCommitmentResolver().resolve([budget, recommendation, confirmed, matched])
    assert len(resolved) == 1
    assert resolved[0].source == "matched_transaction"


def test_confirmed_beats_recommendation_and_budget() -> None:
    tax_period_id = uuid4()
    confirmed = PlanningCommitment(
        source="confirmed_cash_plan_item",
        amount=Decimal("10000.00"),
        tax_period_id=tax_period_id,
        linked_entity_type="tax_period",
        linked_entity_id=tax_period_id,
    )
    recommendation = PlanningCommitment(
        source="linked_module_recommendation",
        amount=Decimal("10000.00"),
        tax_period_id=tax_period_id,
    )
    resolved = PlanningCommitmentResolver().resolve([recommendation, confirmed])
    assert len(resolved) == 1
    assert resolved[0].source == "confirmed_cash_plan_item"


def test_distinct_entities_are_kept() -> None:
    a = PlanningCommitment(
        source="planned_cash_plan_item",
        amount=Decimal("100.00"),
        goal_id=uuid4(),
    )
    b = PlanningCommitment(
        source="planned_cash_plan_item",
        amount=Decimal("200.00"),
        goal_id=uuid4(),
    )
    resolved = PlanningCommitmentResolver().resolve([a, b])
    assert len(resolved) == 2


def test_ignores_cancelled_and_archived() -> None:
    debt_id = uuid4()
    cancelled = PlanningCommitment(
        source="confirmed_cash_plan_item",
        amount=Decimal("500.00"),
        debt_id=debt_id,
        cancelled=True,
    )
    fallback = PlanningCommitment(
        source="budget_allocation",
        amount=Decimal("500.00"),
        debt_id=debt_id,
    )
    resolved = PlanningCommitmentResolver().resolve([cancelled, fallback])
    assert len(resolved) == 1
    assert resolved[0].source == "budget_allocation"
