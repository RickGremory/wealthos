"""Payment strategy request/response schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from wealthos.modules.debts.application.queries.get_debt_strategy import DebtStrategyView


class DebtStrategyUpdate(BaseModel):
    strategy: Literal["avalanche", "snowball", "minimum_only", "manual"]


class StrategySummaryResponse(BaseModel):
    active_commitments: int
    total_balance: Decimal
    currency: str


class StrategyNextActionResponse(BaseModel):
    type: str
    commitment_id: UUID | None = None
    amount: Decimal | None = None
    due_date: date | None = None
    reason_code: str


class StrategyRankingItemResponse(BaseModel):
    position: int
    commitment_id: UUID
    name: str
    reason_code: str
    eligible: bool = True


class DebtStrategyResponse(BaseModel):
    status: str
    strategy: str
    generated_at: datetime
    summary: StrategySummaryResponse | None = None
    next_action: StrategyNextActionResponse | None = None
    ranking: list[StrategyRankingItemResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    excluded_commitments: int = 0

    @classmethod
    def from_view(cls, view: DebtStrategyView) -> DebtStrategyResponse:
        proj = view.projection
        summary = None
        if view.summary is not None:
            summary = StrategySummaryResponse(
                active_commitments=view.summary.active_commitments,
                total_balance=view.summary.total_balance,
                currency=view.summary.currency,
            )
        next_action = None
        if view.next_action is not None:
            next_action = StrategyNextActionResponse(
                type=view.next_action.type.value,
                commitment_id=view.recommended_commitment_id,
                amount=view.next_action.amount,
                due_date=view.next_action.due_date,
                reason_code=view.next_action.reason_code,
            )
        ranking = [
            StrategyRankingItemResponse(
                position=item.position,
                commitment_id=item.debt.id,
                name=item.debt.name.value,
                reason_code=item.reason_code,
                eligible=item.eligible,
            )
            for item in proj.ranking
        ]
        return cls(
            status=proj.status,
            strategy=proj.strategy,
            generated_at=view.generated_at,
            summary=summary,
            next_action=next_action,
            ranking=ranking,
            warnings=list(proj.warnings),
            excluded_commitments=proj.excluded_commitments,
        )
