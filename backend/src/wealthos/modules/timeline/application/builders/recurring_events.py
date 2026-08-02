"""Build FinancialEvents from recurring rule lifecycle."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from wealthos.shared.events import FinancialEvent


def build_recurring_rule_created_event(
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    occurred_at: datetime,
    currency: str | None = None,
    direction: str | None = None,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="recurring",
        event_type="recurring.rule.created",
        importance="high",
        title="Nuevo recurrente",
        description=f"Se creó la regla «{name}».",
        resource_type="recurring_rule",
        resource_id=rule_id,
        currency=currency,
        metadata={"name": name, "direction": direction},
    )


def build_recurring_rule_paused_event(
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    occurred_at: datetime,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="recurring",
        event_type="recurring.rule.paused",
        importance="high",
        title="Recurrente pausado",
        description=f"«{name}» quedó en pausa.",
        resource_type="recurring_rule",
        resource_id=rule_id,
        metadata={"name": name},
    )


def build_recurring_rule_resumed_event(
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    occurred_at: datetime,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="recurring",
        event_type="recurring.rule.resumed",
        importance="high",
        title="Recurrente reanudado",
        description=f"«{name}» volvió a estar activo.",
        resource_type="recurring_rule",
        resource_id=rule_id,
        metadata={"name": name},
    )


def build_recurring_rule_ended_event(
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    occurred_at: datetime,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="recurring",
        event_type="recurring.rule.ended",
        importance="critical",
        title="Recurrente finalizado",
        description=f"Se finalizó la regla «{name}».",
        resource_type="recurring_rule",
        resource_id=rule_id,
        metadata={"name": name},
    )


def build_recurring_rule_archived_event(
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    occurred_at: datetime,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="recurring",
        event_type="recurring.rule.archived",
        importance="normal",
        title="Recurrente archivado",
        description=f"«{name}» se archivó.",
        resource_type="recurring_rule",
        resource_id=rule_id,
        metadata={"name": name},
    )


def build_recurring_rule_versioned_event(
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    occurred_at: datetime,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="recurring",
        event_type="recurring.rule.versioned",
        importance="high",
        title="Recurrente versionado",
        description=f"Se aplicó un cambio estructural a «{name}».",
        resource_type="recurring_rule",
        resource_id=rule_id,
        metadata={"name": name},
    )


def build_recurring_exception_created_event(
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    occurred_at: datetime,
    exception_type: str,
) -> FinancialEvent:
    labels = {
        "skip": ("Ocurrencia omitida", f"Se omitió una ocurrencia de «{name}»."),
        "reschedule": ("Ocurrencia reprogramada", f"Se reprogramó una ocurrencia de «{name}»."),
        "amount_override": (
            "Monto de ocurrencia ajustado",
            f"Se ajustó el monto de una ocurrencia de «{name}».",
        ),
    }
    title, description = labels.get(
        exception_type,
        ("Excepción de recurrente", f"Se registró una excepción en «{name}»."),
    )
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="recurring",
        event_type="recurring.exception.created",
        importance="normal",
        title=title,
        description=description,
        resource_type="recurring_rule",
        resource_id=rule_id,
        metadata={"name": name, "exception_type": exception_type},
    )


def build_recurring_settlement_linked_event(
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    occurred_at: datetime,
    transaction_id: UUID,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="recurring",
        event_type="recurring.settlement.linked",
        importance="high",
        title="Recurrente confirmado",
        description=f"Se vinculó una transacción a «{name}».",
        resource_type="recurring_rule",
        resource_id=rule_id,
        metadata={"name": name, "transaction_id": str(transaction_id)},
    )


def build_recurring_settlement_unlinked_event(
    *,
    organization_id: UUID,
    rule_id: UUID,
    name: str,
    occurred_at: datetime,
) -> FinancialEvent:
    return FinancialEvent(
        organization_id=organization_id,
        occurred_at=occurred_at,
        source_type="recurring",
        event_type="recurring.settlement.unlinked",
        importance="normal",
        title="Vínculo de recurrente anulado",
        description=f"Se anuló el vínculo de liquidación de «{name}».",
        resource_type="recurring_rule",
        resource_id=rule_id,
        metadata={"name": name},
    )
