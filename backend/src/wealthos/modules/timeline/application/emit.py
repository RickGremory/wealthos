"""Helpers to emit FinancialEvents from other modules' write paths."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.timeline.application.builders.commitment_events import (
    build_commitment_archived_event,
    build_commitment_closed_event,
    build_commitment_created_event,
    build_commitment_paused_event,
    build_commitment_payment_event,
    build_commitment_resumed_event,
    build_commitment_strategy_changed_event,
)
from wealthos.modules.timeline.application.builders.goal_events import (
    build_goal_completed_event,
    build_goal_created_event,
    build_goal_milestone_event,
    crossed_milestones,
)
from wealthos.modules.timeline.application.builders.recurring_events import (
    build_recurring_exception_created_event,
    build_recurring_rule_archived_event,
    build_recurring_rule_created_event,
    build_recurring_rule_ended_event,
    build_recurring_rule_paused_event,
    build_recurring_rule_resumed_event,
    build_recurring_rule_versioned_event,
    build_recurring_settlement_linked_event,
    build_recurring_settlement_unlinked_event,
)
from wealthos.modules.timeline.application.builders.transaction_events import (
    build_transaction_posted_event,
    resolve_transfer_destination_id,
)
from wealthos.modules.timeline.application.publisher import EventPublisher
from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.shared.events import FinancialEvent


def emit_transaction_posted(
    publisher: EventPublisher,
    accounts: AccountRepository,
    tx: Transaction,
) -> None:
    destination = None
    dest_id = resolve_transfer_destination_id(tx)
    if dest_id is not None:
        destination = accounts.get_by_id(tx.organization_id, dest_id)
    event = build_transaction_posted_event(tx, destination_account=destination)
    if event is not None:
        publisher.publish(event)


def emit_commitment_created(
    publisher: EventPublisher,
    *,
    organization_id: UUID,
    commitment_id: UUID,
    name: str,
    occurred_at: datetime,
    currency: str | None = None,
    principal: Decimal | None = None,
) -> None:
    publisher.publish(
        build_commitment_created_event(
            organization_id=organization_id,
            commitment_id=commitment_id,
            name=name,
            occurred_at=occurred_at,
            currency=currency,
            principal=principal,
        )
    )


def emit_commitment_lifecycle(
    publisher: EventPublisher,
    *,
    action: str,
    organization_id: UUID,
    commitment_id: UUID,
    name: str,
    occurred_at: datetime | None = None,
    strategy: str | None = None,
) -> None:
    when = occurred_at or datetime.now(UTC)
    builders = {
        "paused": build_commitment_paused_event,
        "resumed": build_commitment_resumed_event,
        "closed": build_commitment_closed_event,
        "archived": build_commitment_archived_event,
    }
    if action == "strategy_changed":
        assert strategy is not None
        publisher.publish(
            build_commitment_strategy_changed_event(
                organization_id=organization_id,
                commitment_id=commitment_id,
                name=name,
                strategy=strategy,
                occurred_at=when,
            )
        )
        return
    builder = builders[action]
    publisher.publish(
        builder(
            organization_id=organization_id,
            commitment_id=commitment_id,
            name=name,
            occurred_at=when,
        )
    )


def emit_commitment_payment(
    publisher: EventPublisher,
    *,
    organization_id: UUID,
    commitment_id: UUID,
    name: str,
    occurred_at: datetime,
    amount: Decimal,
    currency: str,
    transaction_id: UUID,
) -> None:
    publisher.publish(
        build_commitment_payment_event(
            organization_id=organization_id,
            commitment_id=commitment_id,
            name=name,
            occurred_at=occurred_at,
            amount=amount,
            currency=currency,
            transaction_id=transaction_id,
        )
    )


def emit_goal_created(
    publisher: EventPublisher,
    *,
    organization_id: UUID,
    goal_id: UUID,
    name: str,
    occurred_at: datetime,
    currency: str,
    target_amount: Decimal,
) -> None:
    publisher.publish(
        build_goal_created_event(
            organization_id=organization_id,
            goal_id=goal_id,
            name=name,
            occurred_at=occurred_at,
            currency=currency,
            target_amount=target_amount,
        )
    )


def emit_goal_progress(
    publisher: EventPublisher,
    *,
    organization_id: UUID,
    goal_id: UUID,
    name: str,
    occurred_at: datetime,
    currency: str,
    previous_percent: float,
    current_percent: float,
    current_amount: Decimal | None,
    status: str,
) -> None:
    events: list[FinancialEvent] = []
    for percent in crossed_milestones(previous_percent, current_percent):
        events.append(
            build_goal_milestone_event(
                organization_id=organization_id,
                goal_id=goal_id,
                name=name,
                occurred_at=occurred_at,
                currency=currency,
                percent=percent,
                current_amount=current_amount,
            )
        )
    if status == "completed" and previous_percent < 100:
        # Prefer dedicated completed event if milestone_100 wasn't already emitted.
        if not any(e.event_type == "goal.milestone_100" for e in events):
            events.append(
                build_goal_completed_event(
                    organization_id=organization_id,
                    goal_id=goal_id,
                    name=name,
                    occurred_at=occurred_at,
                    currency=currency,
                )
            )
    publisher.publish_many(events)


def emit_recurring_rule_created(
    publisher: EventPublisher,
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    occurred_at: datetime,
    currency: str | None = None,
    direction: str | None = None,
) -> None:
    publisher.publish(
        build_recurring_rule_created_event(
            organization_id=organization_id,
            rule_id=rule_id,
            name=name,
            occurred_at=occurred_at,
            currency=currency,
            direction=direction,
        )
    )


def emit_recurring_lifecycle(
    publisher: EventPublisher,
    *,
    action: str,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    occurred_at: datetime | None = None,
) -> None:
    when = occurred_at or datetime.now(UTC)
    builders = {
        "paused": build_recurring_rule_paused_event,
        "resumed": build_recurring_rule_resumed_event,
        "ended": build_recurring_rule_ended_event,
        "archived": build_recurring_rule_archived_event,
        "versioned": build_recurring_rule_versioned_event,
    }
    builder = builders[action]
    publisher.publish(
        builder(
            organization_id=organization_id,
            rule_id=rule_id,
            name=name,
            occurred_at=when,
        )
    )


def emit_recurring_exception_created(
    publisher: EventPublisher,
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    exception_type: str,
    occurred_at: datetime | None = None,
) -> None:
    publisher.publish(
        build_recurring_exception_created_event(
            organization_id=organization_id,
            rule_id=rule_id,
            name=name,
            occurred_at=occurred_at or datetime.now(UTC),
            exception_type=exception_type,
        )
    )


def emit_recurring_settlement_linked(
    publisher: EventPublisher,
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    transaction_id: UUID,
    occurred_at: datetime | None = None,
) -> None:
    publisher.publish(
        build_recurring_settlement_linked_event(
            organization_id=organization_id,
            rule_id=rule_id,
            name=name,
            occurred_at=occurred_at or datetime.now(UTC),
            transaction_id=transaction_id,
        )
    )


def emit_recurring_settlement_unlinked(
    publisher: EventPublisher,
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    occurred_at: datetime | None = None,
) -> None:
    publisher.publish(
        build_recurring_settlement_unlinked_event(
            organization_id=organization_id,
            rule_id=rule_id,
            name=name,
            occurred_at=occurred_at or datetime.now(UTC),
        )
    )
