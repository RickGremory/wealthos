"""DebtPayment — metadata complementing a transfer Transaction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.debts.domain.exceptions import (
    DebtPaymentAmountInvalid,
    DebtPaymentBreakdownInvalid,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(slots=True)
class DebtPayment:
    id: UUID
    organization_id: UUID
    debt_id: UUID
    transaction_id: UUID
    amount: Money
    principal_amount: Money | None
    interest_amount: Money | None
    paid_at: datetime
    created_by_user_id: UUID
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        debt_id: UUID,
        transaction_id: UUID,
        amount: Money,
        paid_at: datetime,
        created_by_user_id: UUID,
        principal_amount: Money | None = None,
        interest_amount: Money | None = None,
        payment_id: UUID | None = None,
    ) -> DebtPayment:
        if amount.amount <= Decimal("0.00"):
            raise DebtPaymentAmountInvalid("Payment amount must be positive.")

        if (principal_amount is None) ^ (interest_amount is None):
            raise DebtPaymentBreakdownInvalid(
                "Provide both principal_amount and interest_amount, or neither."
            )
        if principal_amount is not None and interest_amount is not None:
            if principal_amount.currency != amount.currency:
                raise DebtPaymentBreakdownInvalid(
                    "Principal currency must match payment currency."
                )
            if interest_amount.currency != amount.currency:
                raise DebtPaymentBreakdownInvalid(
                    "Interest currency must match payment currency."
                )
            if principal_amount.amount < 0 or interest_amount.amount < 0:
                raise DebtPaymentBreakdownInvalid(
                    "Principal and interest amounts cannot be negative."
                )
            if principal_amount.amount + interest_amount.amount != amount.amount:
                raise DebtPaymentBreakdownInvalid(
                    "principal_amount + interest_amount must equal amount."
                )

        return cls(
            id=payment_id or uuid4(),
            organization_id=organization_id,
            debt_id=debt_id,
            transaction_id=transaction_id,
            amount=amount,
            principal_amount=principal_amount,
            interest_amount=interest_amount,
            paid_at=paid_at,
            created_by_user_id=created_by_user_id,
            created_at=datetime.now(UTC),
        )
