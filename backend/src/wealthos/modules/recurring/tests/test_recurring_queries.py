"""Query-layer tests for Recurring list/preview."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from wealthos.modules.recurring.application.commands.create_rule import (
    CreateRecurringRuleCommand,
    CreateRecurringRuleHandler,
)
from wealthos.modules.recurring.application.queries.list_get_rules import (
    GetRecurringRuleInput,
    GetRecurringRuleQuery,
    ListRecurringRulesInput,
    ListRecurringRulesQuery,
)
from wealthos.modules.recurring.application.queries.preview_occurrences import (
    ListRecurringOccurrencesInput,
    ListRecurringOccurrencesQuery,
    PreviewUnsavedRecurringRuleInput,
    PreviewUnsavedRecurringRuleQuery,
)
from wealthos.modules.recurring.domain.enums.recurrence import RecurrenceFrequency
from wealthos.modules.recurring.domain.enums.rule import RecurringDirection
from wealthos.modules.recurring.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)
from wealthos.modules.recurring.tests.test_recurring_commands import (
    FakeAccounts,
    InMemoryRecurringAggregateRepository,
)


def test_list_and_get_rule() -> None:
    repo = InMemoryRecurringAggregateRepository()
    created = CreateRecurringRuleHandler(repo, accounts=FakeAccounts()).execute(
        CreateRecurringRuleCommand(
            organization_id=uuid4(),
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
    listed = ListRecurringRulesQuery(repo).execute(
        ListRecurringRulesInput(
            organization_id=created.organization_id,
            evaluated_on=date(2026, 8, 1),
            timezone="America/Merida",
        )
    )
    assert len(listed) == 1
    assert listed[0].name == "Internet"
    assert listed[0].next_occurrence is not None
    assert listed[0].next_occurrence.expected_on == date(2026, 8, 15)

    detail = GetRecurringRuleQuery(repo).execute(
        GetRecurringRuleInput(
            organization_id=created.organization_id,
            rule_id=created.id,
            evaluated_on=date(2026, 8, 1),
            timezone="America/Merida",
        )
    )
    assert detail.current_version.amount == "800.00"
    assert len(detail.upcoming_occurrences) >= 1


def test_preview_unsaved_and_list_occurrences() -> None:
    preview = PreviewUnsavedRecurringRuleQuery().execute(
        PreviewUnsavedRecurringRuleInput(
            organization_id=uuid4(),
            period_start=date(2026, 8, 1),
            period_end=date(2026, 10, 31),
            evaluated_on=date(2026, 8, 1),
            timezone="America/Merida",
            name="Renta",
            direction=RecurringDirection.OUTFLOW,
            amount=Decimal("10000"),
            currency="MXN",
            pattern=RecurrencePattern(
                frequency=RecurrenceFrequency.MONTHLY,
                interval=1,
                day_of_month=1,
            ),
            starts_on=date(2026, 8, 1),
        )
    )
    assert preview.dates == (date(2026, 8, 1), date(2026, 9, 1), date(2026, 10, 1))

    repo = InMemoryRecurringAggregateRepository()
    created = CreateRecurringRuleHandler(repo, accounts=FakeAccounts()).execute(
        CreateRecurringRuleCommand(
            organization_id=uuid4(),
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
    occurrences = ListRecurringOccurrencesQuery(repo).execute(
        ListRecurringOccurrencesInput(
            organization_id=created.organization_id,
            period_start=date(2026, 8, 1),
            period_end=date(2026, 9, 30),
            evaluated_on=date(2026, 8, 1),
            timezone="America/Merida",
            currency="MXN",
        )
    )
    assert [item.expected_on for item in occurrences] == [
        date(2026, 8, 15),
        date(2026, 9, 15),
    ]
