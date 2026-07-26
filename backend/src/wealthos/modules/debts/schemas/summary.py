"""Debt summary response schema."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from wealthos.modules.debts.application.queries.get_debt_summary import DebtSummary


class DebtSummaryByCurrencyResponse(BaseModel):
    currency: str
    total_debt: Decimal
    total_minimum_payments: Decimal
    weighted_average_rate: Decimal
    active_debt_count: int
    highest_interest_debt_id: UUID | None
    highest_interest_rate: Decimal | None


class CommitmentUpcomingDueResponse(BaseModel):
    commitment_id: UUID
    name: str
    currency: str
    due_date: date
    days_until_due: int
    amount: Decimal | None = None


class CommitmentAttentionItemResponse(BaseModel):
    commitment_id: UUID
    code: str
    message: str
    name: str


class DebtSummaryResponse(BaseModel):
    by_currency: list[DebtSummaryByCurrencyResponse]
    groups: list[DebtSummaryByCurrencyResponse] = Field(default_factory=list)
    active_commitments: int = 0
    commitments_needing_attention: int = 0
    next_due: CommitmentUpcomingDueResponse | None = None
    attention: list[CommitmentAttentionItemResponse] = Field(default_factory=list)

    @classmethod
    def from_summary(cls, summary: DebtSummary) -> DebtSummaryResponse:
        groups = [
            DebtSummaryByCurrencyResponse(
                currency=item.currency,
                total_debt=item.total_debt,
                total_minimum_payments=item.total_minimum_payments,
                weighted_average_rate=item.weighted_average_rate,
                active_debt_count=item.active_debt_count,
                highest_interest_debt_id=item.highest_interest_debt_id,
                highest_interest_rate=item.highest_interest_rate,
            )
            for item in summary.by_currency
        ]
        next_due = None
        if summary.next_due is not None:
            nd = summary.next_due
            next_due = CommitmentUpcomingDueResponse(
                commitment_id=nd.commitment_id,
                name=nd.name,
                currency=nd.currency,
                due_date=nd.due_date,
                days_until_due=nd.days_until_due,
                amount=nd.amount,
            )
        attention = [
            CommitmentAttentionItemResponse(
                commitment_id=item.commitment_id,
                code=item.code,
                message=item.message,
                name=item.name,
            )
            for item in summary.attention
        ]
        return cls(
            by_currency=groups,
            groups=groups,
            active_commitments=summary.active_commitments,
            commitments_needing_attention=summary.commitments_needing_attention,
            next_due=next_due,
            attention=attention,
        )
