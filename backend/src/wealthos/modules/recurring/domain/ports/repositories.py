"""Persistence ports for Recurring (SPEC-005 PR1)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol
from uuid import UUID

from wealthos.modules.recurring.domain.entities.occurrence_settlement import (
    RecurringOccurrenceSettlement,
)
from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
)
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringDirection,
    RecurringRuleStatus,
    RecurringSourceType,
)


@dataclass(frozen=True, slots=True)
class RecurringRuleFilters:
    status: RecurringRuleStatus | None = None
    direction: RecurringDirection | None = None
    currency: str | None = None
    source_type: RecurringSourceType | None = None
    include_archived: bool = False
    account_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class RecurringRuleListProjection:
    """Lightweight list row (current version snapshot)."""

    rule_id: UUID
    organization_id: UUID
    name: str
    direction: RecurringDirection
    amount: str
    currency: str
    status: RecurringRuleStatus
    source_type: RecurringSourceType
    frequency: str
    interval: int
    version: int


class RecurringAggregateRepository(Protocol):
    def add(self, aggregate: RecurringAggregate) -> RecurringAggregate: ...

    def get(
        self,
        organization_id: UUID,
        rule_id: UUID,
        *,
        for_update: bool = False,
    ) -> RecurringAggregate | None: ...

    def save(
        self,
        aggregate: RecurringAggregate,
        expected_version: int,
    ) -> RecurringAggregate: ...

    def list(
        self,
        organization_id: UUID,
        filters: RecurringRuleFilters,
    ) -> list[RecurringRuleListProjection]: ...

    def list_aggregates(
        self,
        organization_id: UUID,
        filters: RecurringRuleFilters,
    ) -> list[RecurringAggregate]: ...


class RecurringSettlementRepository(Protocol):
    def add(self, settlement: RecurringOccurrenceSettlement) -> RecurringOccurrenceSettlement: ...

    def list_for_occurrence(
        self,
        organization_id: UUID,
        occurrence_key: str,
        *,
        include_voided: bool = False,
    ) -> list[RecurringOccurrenceSettlement]: ...

    def list_for_keys(
        self,
        organization_id: UUID,
        occurrence_keys: tuple[str, ...],
        *,
        include_voided: bool = False,
    ) -> list[RecurringOccurrenceSettlement]: ...

    def get_by_id(
        self,
        organization_id: UUID,
        settlement_id: UUID,
    ) -> RecurringOccurrenceSettlement | None: ...

    def list_for_transaction(
        self,
        organization_id: UUID,
        transaction_id: UUID,
        *,
        include_voided: bool = False,
    ) -> list[RecurringOccurrenceSettlement]: ...

    def save(self, settlement: RecurringOccurrenceSettlement) -> RecurringOccurrenceSettlement: ...


class RecurringExceptionReadRepository(Protocol):
    def list_affecting_period(
        self,
        organization_id: UUID,
        rule_id: UUID,
        period_start: date,
        period_end: date,
    ) -> list: ...
