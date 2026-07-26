"""Build FinancialEvents from posted transactions."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.shared.events import FinancialEvent

# Expenses below this absolute amount (per currency unit) are importance=low.
MIN_SIGNIFICANT_EXPENSE = Decimal("50.00")


def _primary_amount(tx: Transaction) -> tuple[Decimal | None, str | None]:
    if not tx.entries:
        return None, None
    entry = tx.entries[0]
    return abs(entry.amount.amount), entry.amount.currency.value


def build_transaction_posted_event(
    tx: Transaction,
    *,
    destination_account: Account | None = None,
) -> FinancialEvent | None:
    """Return a FinancialEvent for a newly posted transaction, or None if skipped."""
    amount, currency = _primary_amount(tx)
    tx_type = str(tx.transaction_type)
    description = str(tx.description)

    if tx_type == "income":
        return FinancialEvent(
            organization_id=tx.organization_id,
            occurred_at=tx.occurred_at,
            source_type="transaction",
            event_type="transaction.income_posted",
            importance="high",
            title="Ingreso registrado",
            description=description,
            resource_type="transaction",
            resource_id=tx.id,
            currency=currency,
            amount=amount,
            metadata={"transaction_type": tx_type},
        )

    if tx_type == "expense":
        magnitude = amount or Decimal("0")
        importance = "normal" if magnitude >= MIN_SIGNIFICANT_EXPENSE else "low"
        return FinancialEvent(
            organization_id=tx.organization_id,
            occurred_at=tx.occurred_at,
            source_type="transaction",
            event_type="transaction.expense_posted",
            importance=importance,
            title="Gasto registrado",
            description=description,
            resource_type="transaction",
            resource_id=tx.id,
            currency=currency,
            amount=amount,
            metadata={"transaction_type": tx_type},
        )

    if tx_type == "transfer":
        dest_is_liability = (
            destination_account is not None and destination_account.account_type.is_liability
        )
        if dest_is_liability:
            return FinancialEvent(
                organization_id=tx.organization_id,
                occurred_at=tx.occurred_at,
                source_type="transaction",
                event_type="transaction.liability_transfer_posted",
                importance="high",
                title="Pago a obligación",
                description=description,
                resource_type="transaction",
                resource_id=tx.id,
                currency=currency,
                amount=amount,
                metadata={
                    "transaction_type": tx_type,
                    "destination_account_id": str(destination_account.id)
                    if destination_account
                    else None,
                },
            )
        return FinancialEvent(
            organization_id=tx.organization_id,
            occurred_at=tx.occurred_at,
            source_type="transaction",
            event_type="transaction.transfer_posted",
            importance="normal",
            title="Transferencia",
            description=description,
            resource_type="transaction",
            resource_id=tx.id,
            currency=currency,
            amount=amount,
            metadata={"transaction_type": tx_type},
        )

    # Adjustments: only opening-balance style as normal; others low
    if tx_type == "adjustment":
        is_opening = description.lower().startswith("saldo inicial")
        return FinancialEvent(
            organization_id=tx.organization_id,
            occurred_at=tx.occurred_at,
            source_type="transaction",
            event_type="transaction.adjustment_posted",
            importance="normal" if is_opening else "low",
            title="Saldo inicial" if is_opening else "Ajuste",
            description=description,
            resource_type="transaction",
            resource_id=tx.id,
            currency=currency,
            amount=amount,
            metadata={"transaction_type": tx_type},
        )

    return None


def resolve_transfer_destination_id(tx: Transaction) -> UUID | None:
    if str(tx.transaction_type) != "transfer" or len(tx.entries) < 2:
        return None
    # Transfer: negative on source, positive on destination
    for entry in tx.entries:
        if entry.amount.amount > 0:
            return entry.account_id
    return tx.entries[-1].account_id
