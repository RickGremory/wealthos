"""RecordDebtPayment — transfer + DebtPayment metadata under account locks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.debts.application.services.financial_transfer_service import (
    FinancialTransferService,
)
from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.entities.debt_payment import DebtPayment
from wealthos.modules.debts.domain.exceptions import (
    DebtAccountInactive,
    DebtAccountNotFound,
    DebtNotFoundError,
    DebtPaymentExceedsBalance,
    DebtPaymentSourceInvalid,
)
from wealthos.modules.debts.domain.repositories.debt_payment_repository import (
    DebtPaymentRepository,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class RecordDebtPaymentInput:
    organization_id: UUID
    debt_id: UUID
    source_account_id: UUID
    amount: Decimal
    occurred_at: datetime
    created_by_user_id: UUID
    description: str | None = None
    principal_amount: Decimal | None = None
    interest_amount: Decimal | None = None


@dataclass(frozen=True, slots=True)
class RecordDebtPaymentResult:
    debt: Debt
    payment: DebtPayment


class RecordDebtPaymentCommand:
    def __init__(
        self,
        debts: DebtRepository,
        payments: DebtPaymentRepository,
        accounts: AccountRepository,
        transfers: FinancialTransferService,
    ) -> None:
        self._debts = debts
        self._payments = payments
        self._accounts = accounts
        self._transfers = transfers

    def execute(self, data: RecordDebtPaymentInput) -> RecordDebtPaymentResult:
        debt = self._debts.get_by_id(data.organization_id, data.debt_id)
        if debt is None:
            raise DebtNotFoundError("Debt not found.")
        debt.ensure_accepts_payment()

        if data.source_account_id == debt.account_id:
            raise DebtPaymentSourceInvalid(
                "Source account cannot be the same as the debt account."
            )

        # Deterministic row locks (same ASC order as transfer posting).
        locked = self._accounts.get_many_for_update(
            data.organization_id,
            [data.source_account_id, debt.account_id],
        )
        by_id = {account.id: account for account in locked}
        source = by_id.get(data.source_account_id)
        liability = by_id.get(debt.account_id)
        if source is None:
            raise DebtPaymentSourceInvalid("Source account not found.")
        if liability is None:
            raise DebtAccountNotFound("Debt account not found.")
        if not source.is_active:
            raise DebtPaymentSourceInvalid("Source account is archived.")
        if not liability.is_active:
            raise DebtAccountInactive("Debt account is archived.")
        if source.currency != liability.currency:
            raise DebtPaymentSourceInvalid(
                "Source account currency must match the debt currency."
            )
        if source.account_type.is_liability:
            raise DebtPaymentSourceInvalid(
                "Source account must be an asset account."
            )

        owed = abs(liability.current_balance.amount)
        amount = Money(data.amount, liability.currency)
        if amount.amount > owed:
            raise DebtPaymentExceedsBalance(
                "Payment cannot exceed the outstanding debt balance."
            )

        principal = (
            Money(data.principal_amount, liability.currency)
            if data.principal_amount is not None
            else None
        )
        interest = (
            Money(data.interest_amount, liability.currency)
            if data.interest_amount is not None
            else None
        )

        description = data.description or f"Debt payment: {debt.name.value}"
        transaction_id = self._transfers.transfer(
            organization_id=data.organization_id,
            source_account_id=data.source_account_id,
            destination_account_id=debt.account_id,
            amount=amount,
            occurred_at=data.occurred_at,
            description=description,
            created_by_user_id=data.created_by_user_id,
        )

        payment = DebtPayment.create(
            organization_id=data.organization_id,
            debt_id=debt.id,
            transaction_id=transaction_id,
            amount=amount,
            paid_at=data.occurred_at,
            created_by_user_id=data.created_by_user_id,
            principal_amount=principal,
            interest_amount=interest,
        )
        stored_payment = self._payments.add(payment)

        # Re-read liability balance after transfer posting.
        refreshed = self._accounts.get_by_id(data.organization_id, debt.account_id)
        if refreshed is not None and refreshed.current_balance.amount >= Decimal("0.00"):
            debt.mark_paid_off()
            debt = self._debts.save(debt)

        return RecordDebtPaymentResult(debt=debt, payment=stored_payment)
