"""Create a multi-currency conversion between own accounts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.transactions.application.services.transaction_posting_service import (
    TransactionPostingService,
)
from wealthos.modules.transactions.domain.entities.fx_transfer import FxTransfer
from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.modules.transactions.domain.exceptions import (
    AccountInactive,
    AccountNotFoundError,
    InvalidTransactionEntries,
)
from wealthos.modules.transactions.infrastructure.models.fx_transfer_model import (
    FxTransferModel,
)
from wealthos.shared.domain.value_objects.money import Money

RELATED_TYPE = "fx_transfer"


@dataclass(frozen=True, slots=True)
class CreateFxTransferInput:
    organization_id: UUID
    source_account_id: UUID
    destination_account_id: UUID
    source_amount: Decimal
    destination_amount: Decimal
    occurred_at: datetime
    description: str
    created_by_user_id: UUID
    fee_amount: Decimal | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class CreateFxTransferResult:
    fx_transfer: FxTransfer
    source_transaction: Transaction
    destination_transaction: Transaction
    fee_transaction: Transaction | None


class CreateFxTransferCommand:
    def __init__(
        self,
        *,
        posting: TransactionPostingService,
        accounts: AccountRepository,
        session: Session,
    ) -> None:
        self._posting = posting
        self._accounts = accounts
        self._session = session

    def execute(self, data: CreateFxTransferInput) -> CreateFxTransferResult:
        source = self._accounts.get_by_id(data.organization_id, data.source_account_id)
        destination = self._accounts.get_by_id(
            data.organization_id, data.destination_account_id
        )
        if source is None or destination is None:
            raise AccountNotFoundError("Account not found.")
        if not source.is_active or not destination.is_active:
            raise AccountInactive("Account is archived.")
        source_currency = str(getattr(source.currency, "value", source.currency))
        destination_currency = str(
            getattr(destination.currency, "value", destination.currency)
        )
        if source_currency == destination_currency:
            raise InvalidTransactionEntries(
                "FX conversion requires different currencies."
            )

        fx_id = uuid4()
        label = data.description.strip() or "Conversión de moneda"
        source_tx = Transaction.create_adjustment(
            organization_id=data.organization_id,
            account_id=source.id,
            amount=Money(-abs(data.source_amount), source_currency),
            description=f"{label} · salida",
            occurred_at=data.occurred_at,
            created_by_user_id=data.created_by_user_id,
            notes=data.notes,
        )
        source_tx.attach_source_context(
            source_type="fx_transfer",
            source_occurrence_key=f"fx:{fx_id}:source",
            related_resource_type=RELATED_TYPE,
            related_resource_id=fx_id,
        )
        source_tx = self._posting.post(source_tx)

        destination_tx = Transaction.create_adjustment(
            organization_id=data.organization_id,
            account_id=destination.id,
            amount=Money(abs(data.destination_amount), destination_currency),
            description=f"{label} · entrada",
            occurred_at=data.occurred_at,
            created_by_user_id=data.created_by_user_id,
            notes=data.notes,
        )
        destination_tx.attach_source_context(
            source_type="fx_transfer",
            source_occurrence_key=f"fx:{fx_id}:destination",
            related_resource_type=RELATED_TYPE,
            related_resource_id=fx_id,
        )
        destination_tx = self._posting.post(destination_tx)

        fee_tx: Transaction | None = None
        fee_amount = data.fee_amount
        if fee_amount is not None and fee_amount > 0:
            fee_tx = Transaction.create_adjustment(
                organization_id=data.organization_id,
                account_id=source.id,
                amount=Money(-abs(fee_amount), source_currency),
                description=f"{label} · comisión",
                occurred_at=data.occurred_at,
                created_by_user_id=data.created_by_user_id,
                notes=data.notes,
            )
            fee_tx.attach_source_context(
                source_type="fx_transfer",
                source_occurrence_key=f"fx:{fx_id}:fee",
                related_resource_type=RELATED_TYPE,
                related_resource_id=fx_id,
            )
            fee_tx = self._posting.post(fee_tx)

        entity = FxTransfer.create(
            organization_id=data.organization_id,
            source_account_id=source.id,
            destination_account_id=destination.id,
            source_amount=abs(data.source_amount),
            source_currency=source_currency,
            destination_amount=abs(data.destination_amount),
            destination_currency=destination_currency,
            occurred_at=data.occurred_at,
            description=label,
            created_by_user_id=data.created_by_user_id,
            source_transaction_id=source_tx.id,
            destination_transaction_id=destination_tx.id,
            fee_amount=abs(fee_amount) if fee_amount and fee_amount > 0 else None,
            fee_currency=source_currency if fee_tx is not None else None,
            fee_transaction_id=fee_tx.id if fee_tx is not None else None,
            notes=data.notes,
            fx_id=fx_id,
        )
        model = FxTransferModel(
            id=entity.id,
            organization_id=entity.organization_id,
            source_account_id=entity.source_account_id,
            destination_account_id=entity.destination_account_id,
            source_amount=entity.source_amount,
            source_currency=entity.source_currency,
            destination_amount=entity.destination_amount,
            destination_currency=entity.destination_currency,
            effective_exchange_rate=entity.effective_exchange_rate,
            fee_amount=entity.fee_amount,
            fee_currency=entity.fee_currency,
            occurred_at=entity.occurred_at,
            description=entity.description,
            notes=entity.notes,
            source_transaction_id=entity.source_transaction_id,
            destination_transaction_id=entity.destination_transaction_id,
            fee_transaction_id=entity.fee_transaction_id,
            created_by_user_id=entity.created_by_user_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        self._session.add(model)
        self._session.flush()

        return CreateFxTransferResult(
            fx_transfer=entity,
            source_transaction=source_tx,
            destination_transaction=destination_tx,
            fee_transaction=fee_tx,
        )
