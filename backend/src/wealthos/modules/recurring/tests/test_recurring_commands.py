"""Lifecycle command tests with in-memory repositories."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from wealthos.modules.recurring.application.commands import (
    ArchiveRecurringRuleCommand,
    ArchiveRecurringRuleHandler,
    CreateRecurringOccurrenceExceptionCommand,
    CreateRecurringOccurrenceExceptionHandler,
    CreateRecurringRuleCommand,
    CreateRecurringRuleHandler,
    CreateRecurringRuleVersionCommand,
    CreateRecurringRuleVersionHandler,
    EndRecurringRuleCommand,
    EndRecurringRuleHandler,
    LinkRecurringOccurrenceTransactionCommand,
    LinkRecurringOccurrenceTransactionHandler,
    PauseRecurringRuleCommand,
    PauseRecurringRuleHandler,
    RecurringVersionChanges,
    ResumeRecurringRuleCommand,
    ResumeRecurringRuleHandler,
    UnlinkRecurringOccurrenceTransactionCommand,
    UnlinkRecurringOccurrenceTransactionHandler,
)
from wealthos.modules.recurring.domain.entities.occurrence_settlement import (
    RecurringOccurrenceSettlement,
)
from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
)
from wealthos.modules.recurring.domain.enums.occurrence import (
    RecurringExceptionType,
    RecurringSettlementLinkType,
)
from wealthos.modules.recurring.domain.enums.recurrence import RecurrenceFrequency
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringDirection,
    RecurringRuleStatus,
    RecurringSourceType,
)
from wealthos.modules.recurring.domain.exceptions import (
    PauseAlreadyOpen,
    RecurringConcurrentUpdate,
    RecurringRuleManagedExternally,
    RetroactiveStructuralChangeNotAllowed,
    TransactionAlreadyLinked,
)
from wealthos.modules.recurring.domain.ports.repositories import RecurringRuleFilters
from wealthos.modules.recurring.domain.ports.validation import (
    AccountSnapshot,
    TransactionSnapshot,
)
from wealthos.modules.recurring.domain.value_objects.occurrence_key import OccurrenceKey
from wealthos.modules.recurring.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)


class InMemoryRecurringAggregateRepository:
    def __init__(self) -> None:
        self._items: dict[tuple[UUID, UUID], RecurringAggregate] = {}

    def add(self, aggregate: RecurringAggregate) -> RecurringAggregate:
        stored = deepcopy(aggregate)
        self._items[(stored.organization_id, stored.id)] = stored
        return deepcopy(stored)

    def get(
        self,
        organization_id: UUID,
        rule_id: UUID,
        *,
        for_update: bool = False,
    ) -> RecurringAggregate | None:
        item = self._items.get((organization_id, rule_id))
        return deepcopy(item) if item is not None else None

    def save(
        self,
        aggregate: RecurringAggregate,
        expected_version: int,
    ) -> RecurringAggregate:
        current = self._items.get((aggregate.organization_id, aggregate.id))
        if current is None:
            raise LookupError("missing")
        if current.version != expected_version:
            raise RecurringConcurrentUpdate("conflict")
        if aggregate.version != expected_version + 1:
            raise RecurringConcurrentUpdate("conflict")
        stored = deepcopy(aggregate)
        self._items[(stored.organization_id, stored.id)] = stored
        return deepcopy(stored)

    def list(self, organization_id: UUID, filters: RecurringRuleFilters):
        return []

    def list_aggregates(self, organization_id: UUID, filters: RecurringRuleFilters):
        items = [
            deepcopy(item)
            for (org_id, _), item in self._items.items()
            if org_id == organization_id
        ]
        if filters.status is not None:
            items = [item for item in items if item.rule.status == filters.status]
        elif not filters.include_archived:
            items = [
                item
                for item in items
                if item.rule.status.value != "archived"
            ]
        return items


class InMemorySettlementRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, RecurringOccurrenceSettlement] = {}

    def add(self, settlement: RecurringOccurrenceSettlement) -> RecurringOccurrenceSettlement:
        self._items[settlement.id] = deepcopy(settlement)
        return deepcopy(settlement)

    def list_for_occurrence(
        self,
        organization_id: UUID,
        occurrence_key: str,
        *,
        include_voided: bool = False,
    ) -> list[RecurringOccurrenceSettlement]:
        rows = [
            item
            for item in self._items.values()
            if item.organization_id == organization_id
            and item.occurrence_key == occurrence_key
        ]
        if not include_voided:
            rows = [item for item in rows if not item.is_voided]
        return [deepcopy(item) for item in rows]

    def list_for_keys(self, organization_id, occurrence_keys, *, include_voided=False):
        return []

    def get_by_id(self, organization_id, settlement_id):
        item = self._items.get(settlement_id)
        if item is None or item.organization_id != organization_id:
            return None
        return deepcopy(item)

    def list_for_transaction(
        self,
        organization_id: UUID,
        transaction_id: UUID,
        *,
        include_voided: bool = False,
    ) -> list[RecurringOccurrenceSettlement]:
        rows = [
            item
            for item in self._items.values()
            if item.organization_id == organization_id
            and item.transaction_id == transaction_id
        ]
        if not include_voided:
            rows = [item for item in rows if not item.is_voided]
        return [deepcopy(item) for item in rows]

    def save(self, settlement: RecurringOccurrenceSettlement) -> RecurringOccurrenceSettlement:
        self._items[settlement.id] = deepcopy(settlement)
        return deepcopy(settlement)


class FakeAccounts:
    def get_account(self, organization_id, account_id):
        return AccountSnapshot(
            id=account_id,
            organization_id=organization_id,
            currency="MXN",
            is_active=True,
        )

    def validate_for_rule(self, organization_id, direction, account_id, destination_account_id, currency):
        return None


class FakeTransactions:
    def __init__(self, txn: TransactionSnapshot) -> None:
        self._txn = txn

    def get_transaction(self, organization_id, transaction_id):
        if (
            self._txn.organization_id == organization_id
            and self._txn.id == transaction_id
        ):
            return self._txn
        return None


def _monthly_pattern() -> RecurrencePattern:
    return RecurrencePattern(
        frequency=RecurrenceFrequency.MONTHLY,
        interval=1,
        day_of_month=15,
    )


def _create_internet(repo: InMemoryRecurringAggregateRepository) -> RecurringAggregate:
    handler = CreateRecurringRuleHandler(repo, accounts=FakeAccounts())
    return handler.execute(
        CreateRecurringRuleCommand(
            organization_id=uuid4(),
            actor_id=uuid4(),
            name="Internet",
            direction=RecurringDirection.OUTFLOW,
            amount=Decimal("800.00"),
            currency="MXN",
            pattern=_monthly_pattern(),
            starts_on=date(2026, 7, 15),
            account_id=uuid4(),
        )
    )


def test_create_rule_with_initial_version() -> None:
    repo = InMemoryRecurringAggregateRepository()
    aggregate = _create_internet(repo)
    assert aggregate.rule.status is RecurringRuleStatus.ACTIVE
    assert len(aggregate.versions) == 1
    assert aggregate.versions[0].amount == Decimal("800.00")


def test_create_version_from_future_date() -> None:
    repo = InMemoryRecurringAggregateRepository()
    aggregate = _create_internet(repo)
    handler = CreateRecurringRuleVersionHandler(repo, accounts=FakeAccounts())
    updated = handler.execute(
        CreateRecurringRuleVersionCommand(
            organization_id=aggregate.organization_id,
            actor_id=uuid4(),
            rule_id=aggregate.id,
            effective_from=date(2026, 9, 1),
            today=date(2026, 8, 1),
            expected_version=aggregate.version,
            changes=RecurringVersionChanges(
                name="Internet",
                direction=RecurringDirection.OUTFLOW,
                amount=Decimal("950.00"),
                currency="MXN",
                pattern=_monthly_pattern(),
                starts_on=date(2026, 7, 15),
                account_id=uuid4(),
            ),
        )
    )
    assert updated.versions[0].effective_until == date(2026, 8, 31)
    assert updated.current_version(date(2026, 9, 15)).amount == Decimal("950.00")
    assert updated.current_version(date(2026, 8, 15)).amount == Decimal("800.00")


def test_reject_retroactive_version() -> None:
    repo = InMemoryRecurringAggregateRepository()
    aggregate = _create_internet(repo)
    handler = CreateRecurringRuleVersionHandler(repo)
    with pytest.raises(RetroactiveStructuralChangeNotAllowed):
        handler.execute(
            CreateRecurringRuleVersionCommand(
                organization_id=aggregate.organization_id,
                actor_id=uuid4(),
                rule_id=aggregate.id,
                effective_from=date(2026, 6, 1),
                today=date(2026, 8, 1),
                expected_version=aggregate.version,
                changes=RecurringVersionChanges(
                    name="Internet",
                    direction=RecurringDirection.OUTFLOW,
                    amount=Decimal("950.00"),
                    currency="MXN",
                    pattern=_monthly_pattern(),
                    starts_on=date(2026, 7, 15),
                ),
            )
        )


def test_pause_and_resume() -> None:
    repo = InMemoryRecurringAggregateRepository()
    aggregate = _create_internet(repo)
    paused = PauseRecurringRuleHandler(repo).execute(
        PauseRecurringRuleCommand(
            organization_id=aggregate.organization_id,
            actor_id=uuid4(),
            rule_id=aggregate.id,
            starts_on=date(2026, 8, 1),
            ends_on=None,
            expected_version=aggregate.version,
        )
    )
    assert paused.rule.status is RecurringRuleStatus.PAUSED
    with pytest.raises(PauseAlreadyOpen):
        PauseRecurringRuleHandler(repo).execute(
            PauseRecurringRuleCommand(
                organization_id=aggregate.organization_id,
                actor_id=uuid4(),
                rule_id=aggregate.id,
                starts_on=date(2026, 9, 1),
                ends_on=None,
                expected_version=paused.version,
            )
        )
    resumed = ResumeRecurringRuleHandler(repo).execute(
        ResumeRecurringRuleCommand(
            organization_id=aggregate.organization_id,
            actor_id=uuid4(),
            rule_id=aggregate.id,
            resume_on=date(2026, 9, 1),
            expected_version=paused.version,
        )
    )
    assert resumed.rule.status is RecurringRuleStatus.ACTIVE
    assert resumed.pauses[0].ends_on == date(2026, 8, 31)


def test_skip_exception() -> None:
    repo = InMemoryRecurringAggregateRepository()
    aggregate = _create_internet(repo)
    key = OccurrenceKey.for_recurring_rule(aggregate.id, date(2026, 8, 15)).value
    updated = CreateRecurringOccurrenceExceptionHandler(repo).execute(
        CreateRecurringOccurrenceExceptionCommand(
            organization_id=aggregate.organization_id,
            actor_id=uuid4(),
            rule_id=aggregate.id,
            occurrence_key=key,
            exception_type=RecurringExceptionType.SKIP,
            expected_version=aggregate.version,
            evaluated_on=date(2026, 8, 1),
            timezone="America/Merida",
        )
    )
    assert len(updated.active_exceptions()) == 1


def test_link_and_unlink_settlement() -> None:
    repo = InMemoryRecurringAggregateRepository()
    settlements = InMemorySettlementRepository()
    aggregate = _create_internet(repo)
    key = OccurrenceKey.for_recurring_rule(aggregate.id, date(2026, 8, 15)).value
    txn_id = uuid4()
    txn_port = FakeTransactions(
        TransactionSnapshot(
            id=txn_id,
            organization_id=aggregate.organization_id,
            amount=Decimal("817.00"),
            currency="MXN",
            is_voided=False,
        )
    )
    linked = LinkRecurringOccurrenceTransactionHandler(
        repo,
        settlements,
        txn_port,
    ).execute(
        LinkRecurringOccurrenceTransactionCommand(
            organization_id=aggregate.organization_id,
            actor_id=uuid4(),
            rule_id=aggregate.id,
            occurrence_key=key,
            transaction_id=txn_id,
            link_type=RecurringSettlementLinkType.EXPLICIT,
            evaluated_on=date(2026, 8, 16),
            timezone="America/Merida",
        )
    )
    assert linked.settled_amount == Decimal("817.00")
    with pytest.raises(TransactionAlreadyLinked):
        LinkRecurringOccurrenceTransactionHandler(repo, settlements, txn_port).execute(
            LinkRecurringOccurrenceTransactionCommand(
                organization_id=aggregate.organization_id,
                actor_id=uuid4(),
                rule_id=aggregate.id,
                occurrence_key=key,
                transaction_id=txn_id,
                link_type=RecurringSettlementLinkType.EXPLICIT,
                evaluated_on=date(2026, 8, 16),
                timezone="America/Merida",
            )
        )
    voided = UnlinkRecurringOccurrenceTransactionHandler(settlements).execute(
        UnlinkRecurringOccurrenceTransactionCommand(
            organization_id=aggregate.organization_id,
            actor_id=uuid4(),
            rule_id=aggregate.id,
            settlement_id=linked.id,
        )
    )
    assert voided.is_voided


def test_archive_rejects_externally_managed() -> None:
    repo = InMemoryRecurringAggregateRepository()
    handler = CreateRecurringRuleHandler(repo)
    aggregate = handler.execute(
        CreateRecurringRuleCommand(
            organization_id=uuid4(),
            actor_id=uuid4(),
            name="HSBC",
            direction=RecurringDirection.OUTFLOW,
            amount=Decimal("1000.00"),
            currency="MXN",
            pattern=_monthly_pattern(),
            starts_on=date(2026, 7, 15),
            source_type=RecurringSourceType.COMMITMENT,
            related_resource_type="commitment",
            related_resource_id=uuid4(),
        )
    )
    with pytest.raises(RecurringRuleManagedExternally):
        ArchiveRecurringRuleHandler(repo).execute(
            ArchiveRecurringRuleCommand(
                organization_id=aggregate.organization_id,
                actor_id=uuid4(),
                rule_id=aggregate.id,
                expected_version=aggregate.version,
            )
        )


def test_end_rule() -> None:
    repo = InMemoryRecurringAggregateRepository()
    aggregate = _create_internet(repo)
    ended = EndRecurringRuleHandler(repo).execute(
        EndRecurringRuleCommand(
            organization_id=aggregate.organization_id,
            actor_id=uuid4(),
            rule_id=aggregate.id,
            ends_on=date(2026, 8, 31),
            expected_version=aggregate.version,
            today=date(2026, 9, 1),
        )
    )
    assert ended.rule.status is RecurringRuleStatus.ENDED
    assert ended.versions[0].ends_on == date(2026, 8, 31)


def test_optimistic_lock_conflict() -> None:
    repo = InMemoryRecurringAggregateRepository()
    aggregate = _create_internet(repo)
    with pytest.raises(RecurringConcurrentUpdate):
        PauseRecurringRuleHandler(repo).execute(
            PauseRecurringRuleCommand(
                organization_id=aggregate.organization_id,
                actor_id=uuid4(),
                rule_id=aggregate.id,
                starts_on=date(2026, 8, 1),
                ends_on=date(2026, 8, 10),
                expected_version=aggregate.version + 5,
            )
        )
