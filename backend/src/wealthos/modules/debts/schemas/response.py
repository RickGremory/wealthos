"""Debt and DebtPayment response schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from wealthos.modules.debts.application.views.debt_view import DebtWithBalance
from wealthos.modules.debts.domain.entities.debt_payment import DebtPayment


class DebtResponse(BaseModel):
    id: UUID
    organization_id: UUID
    account_id: UUID
    name: str
    debt_type: str
    currency: str
    annual_interest_rate: Decimal
    minimum_payment: Decimal
    original_principal: Decimal | None
    opened_at: date | None
    maturity_date: date | None
    payment_day: int | None
    statement_day: int | None
    status: str
    notes: str | None
    current_balance: Decimal
    payoff_date: date | None
    months_remaining: int | None
    total_interest: Decimal | None
    total_paid: Decimal | None
    is_payment_sufficient: bool | None
    created_at: datetime
    updated_at: datetime
    paid_off_at: datetime | None
    archived_at: datetime | None

    @classmethod
    def from_debt_with_balance(cls, item: DebtWithBalance) -> DebtResponse:
        debt = item.debt
        payoff = item.payoff
        return cls(
            id=debt.id,
            organization_id=debt.organization_id,
            account_id=debt.account_id,
            name=debt.name.value,
            debt_type=debt.debt_type.value,
            currency=debt.minimum_payment.currency.value,
            annual_interest_rate=debt.annual_interest_rate.annual_percentage,
            minimum_payment=debt.minimum_payment.amount,
            original_principal=(
                debt.original_principal.amount if debt.original_principal else None
            ),
            opened_at=debt.opened_at,
            maturity_date=debt.maturity_date,
            payment_day=debt.payment_day,
            statement_day=debt.statement_day,
            status=debt.status.value,
            notes=debt.notes,
            current_balance=item.current_balance.amount,
            payoff_date=payoff.payoff_date if payoff else None,
            months_remaining=payoff.months_remaining if payoff else None,
            total_interest=payoff.total_interest if payoff else None,
            total_paid=payoff.total_paid if payoff else None,
            is_payment_sufficient=payoff.is_payment_sufficient if payoff else None,
            created_at=debt.created_at,
            updated_at=debt.updated_at,
            paid_off_at=debt.paid_off_at,
            archived_at=debt.archived_at,
        )


class DebtListResponse(BaseModel):
    items: list[DebtResponse]
    total: int


class DebtPaymentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    debt_id: UUID
    transaction_id: UUID
    amount: Decimal
    currency: str
    principal_amount: Decimal | None
    interest_amount: Decimal | None
    paid_at: datetime
    created_by_user_id: UUID
    created_at: datetime

    @classmethod
    def from_entity(cls, payment: DebtPayment) -> DebtPaymentResponse:
        return cls(
            id=payment.id,
            organization_id=payment.organization_id,
            debt_id=payment.debt_id,
            transaction_id=payment.transaction_id,
            amount=payment.amount.amount,
            currency=payment.amount.currency.value,
            principal_amount=(
                payment.principal_amount.amount if payment.principal_amount else None
            ),
            interest_amount=(payment.interest_amount.amount if payment.interest_amount else None),
            paid_at=payment.paid_at,
            created_by_user_id=payment.created_by_user_id,
            created_at=payment.created_at,
        )


class DebtPaymentListResponse(BaseModel):
    items: list[DebtPaymentResponse]
    total: int
    limit: int
    offset: int
