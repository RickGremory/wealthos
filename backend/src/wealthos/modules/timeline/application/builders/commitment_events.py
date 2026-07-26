"""Build FinancialEvents from commitment (debt) lifecycle."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from wealthos.shared.events import FinancialEvent


def build_commitment_created_event(
    *,
    organization_id: UUID,
    commitment_id: UUID,
    name: str,
    occurred_at: datetime,
    currency: str | None = None,
    principal: Decimal | None = None,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="commitment",
        event_type="commitment.created",
        importance="high",
        title="Nueva obligación",
        description=f"Se registró la obligación «{name}».",
        resource_type="commitment",
        resource_id=commitment_id,
        currency=currency,
        amount=principal,
        metadata={"name": name},
    )


def build_commitment_paused_event(
    *,
    organization_id: UUID,
    commitment_id: UUID,
    name: str,
    occurred_at: datetime,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="commitment",
        event_type="commitment.paused",
        importance="high",
        title="Obligación pausada",
        description=f"«{name}» quedó en pausa.",
        resource_type="commitment",
        resource_id=commitment_id,
        metadata={"name": name},
    )


def build_commitment_resumed_event(
    *,
    organization_id: UUID,
    commitment_id: UUID,
    name: str,
    occurred_at: datetime,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="commitment",
        event_type="commitment.resumed",
        importance="high",
        title="Obligación reanudada",
        description=f"«{name}» volvió a estar activa.",
        resource_type="commitment",
        resource_id=commitment_id,
        metadata={"name": name},
    )


def build_commitment_closed_event(
    *,
    organization_id: UUID,
    commitment_id: UUID,
    name: str,
    occurred_at: datetime,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="commitment",
        event_type="commitment.closed",
        importance="critical",
        title="Obligación cerrada",
        description=f"Se cerró la obligación «{name}».",
        resource_type="commitment",
        resource_id=commitment_id,
        metadata={"name": name},
    )


def build_commitment_archived_event(
    *,
    organization_id: UUID,
    commitment_id: UUID,
    name: str,
    occurred_at: datetime,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="commitment",
        event_type="commitment.archived",
        importance="normal",
        title="Obligación archivada",
        description=f"«{name}» se archivó.",
        resource_type="commitment",
        resource_id=commitment_id,
        metadata={"name": name},
    )


def build_commitment_strategy_changed_event(
    *,
    organization_id: UUID,
    commitment_id: UUID,
    name: str,
    strategy: str,
    occurred_at: datetime,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="commitment",
        event_type="commitment.strategy_changed",
        importance="high",
        title="Estrategia de pago actualizada",
        description=f"La estrategia de «{name}» cambió a {strategy}.",
        resource_type="commitment",
        resource_id=commitment_id,
        metadata={"name": name, "strategy": strategy},
    )


def build_commitment_payment_event(
    *,
    organization_id: UUID,
    commitment_id: UUID,
    name: str,
    occurred_at: datetime,
    amount: Decimal,
    currency: str,
    transaction_id: UUID,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="commitment",
        event_type="commitment.payment_posted",
        importance="high",
        title="Pago de obligación",
        description=f"Pago registrado en «{name}».",
        resource_type="commitment",
        resource_id=commitment_id,
        currency=currency,
        amount=amount,
        metadata={
            "name": name,
            "transaction_id": str(transaction_id),
        },
    )
