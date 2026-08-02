"""Unit tests for Recurring Planning / Calendar / Dashboard adapters."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.domain.enums.cash_flow import CashFlowDirection
from wealthos.modules.planning.domain.ports.source_adapter import PlanningCollectionRequest
from wealthos.modules.planning.infrastructure.adapters.recurring import (
    RecurringPlanningAdapter,
)
from wealthos.modules.recurring.application.commands.create_rule import (
    CreateRecurringRuleCommand,
    CreateRecurringRuleHandler,
)
from wealthos.modules.recurring.domain.enums.recurrence import RecurrenceFrequency
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringDirection,
    RecurringSourceType,
)
from wealthos.modules.recurring.domain.value_objects.occurrence_key import OccurrenceKey
from wealthos.modules.recurring.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)
from wealthos.modules.recurring.infrastructure.calendar.recurring_calendar_adapter import (
    RecurringCalendarAdapter,
)
from wealthos.modules.recurring.infrastructure.planning.recurring_dashboard_adapter import (
    RecurringDashboardAdapter,
)
from wealthos.modules.recurring.tests.test_recurring_commands import (
    FakeAccounts,
    InMemoryRecurringAggregateRepository,
    InMemorySettlementRepository,
)


def _create_manual(repo: InMemoryRecurringAggregateRepository, org_id):
    return CreateRecurringRuleHandler(repo, accounts=FakeAccounts()).execute(
        CreateRecurringRuleCommand(
            organization_id=org_id,
            actor_id=uuid4(),
            name="Internet",
            direction=RecurringDirection.OUTFLOW,
            amount=Decimal("800.00"),
            currency="MXN",
            pattern=RecurrencePattern(
                frequency=RecurrenceFrequency.MONTHLY,
                interval=1,
                day_of_month=15,
            ),
            starts_on=date(2026, 7, 15),
            account_id=uuid4(),
        )
    )


def _create_external(repo: InMemoryRecurringAggregateRepository, org_id):
    return CreateRecurringRuleHandler(repo, accounts=FakeAccounts()).execute(
        CreateRecurringRuleCommand(
            organization_id=org_id,
            actor_id=uuid4(),
            name="Debt payment",
            direction=RecurringDirection.OUTFLOW,
            amount=Decimal("2000.00"),
            currency="MXN",
            pattern=RecurrencePattern(
                frequency=RecurrenceFrequency.MONTHLY,
                interval=1,
                day_of_month=1,
            ),
            starts_on=date(2026, 7, 1),
            account_id=uuid4(),
            source_type=RecurringSourceType.COMMITMENT,
            related_resource_type="commitment",
            related_resource_id=uuid4(),
        )
    )


def test_planning_adapter_includes_manual_excludes_external() -> None:
    repo = InMemoryRecurringAggregateRepository()
    settlements = InMemorySettlementRepository()
    org_id = uuid4()
    manual = _create_manual(repo, org_id)
    _create_external(repo, org_id)

    adapter = RecurringPlanningAdapter(repo, settlements)
    contribution = adapter.collect(
        PlanningCollectionRequest(
            organization_id=org_id,
            currency="MXN",
            calculated_at=datetime(2026, 8, 1, tzinfo=UTC),
            period_start=datetime(2026, 8, 1, tzinfo=UTC),
            period_end=datetime(2026, 9, 30, tzinfo=UTC),
            settings=PlanningSettings.defaults(org_id),
            timezone="America/Merida",
        )
    )
    keys = {flow.occurrence_key for flow in contribution.cash_flows}
    expected = OccurrenceKey.for_recurring_rule(manual.id, date(2026, 8, 15)).value
    assert expected in keys
    assert all(flow.direction is CashFlowDirection.OUTFLOW for flow in contribution.cash_flows)
    assert all(
        flow.source.resource_type == "recurring_rule" for flow in contribution.cash_flows
    )
    # External commitment-owned rule must not double-count in Recurring source
    assert not any("Debt payment" == flow.label for flow in contribution.cash_flows)


def test_calendar_and_dashboard_share_projector() -> None:
    repo = InMemoryRecurringAggregateRepository()
    settlements = InMemorySettlementRepository()
    org_id = uuid4()
    manual = _create_manual(repo, org_id)

    calendar = RecurringCalendarAdapter(repo, settlements).collect(
        org_id,
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 31),
        today=date(2026, 8, 1),
        timezone="America/Merida",
        currency="MXN",
    )
    assert len(calendar.items) == 1
    assert calendar.items[0].recurring_rule_id == manual.id
    assert calendar.items[0].event_type == "recurring_occurrence"

    dash = RecurringDashboardAdapter(repo, settlements, limit=4).collect(
        org_id,
        currency="MXN",
        today=date(2026, 8, 10),
        timezone="America/Merida",
    )
    assert dash.pending_confirmation_count >= 0
    assert len(dash.upcoming) >= 1
    assert "Internet" in dash.upcoming[0].description
    assert dash.upcoming[0].occurrence_key.startswith(f"recurring:{manual.id}:")
