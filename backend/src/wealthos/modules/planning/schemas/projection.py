"""Cash projection schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, field_serializer

from wealthos.modules.planning.application.queries.get_cash_projection import (
    CashProjectionResult,
)


class CashProjectionPointResponse(BaseModel):
    date: date
    inflows: Decimal
    outflows: Decimal
    ending_balance: Decimal
    lowest_intraday_balance: Decimal

    @field_serializer(
        "inflows",
        "outflows",
        "ending_balance",
        "lowest_intraday_balance",
    )
    def serialize_money(self, value: Decimal) -> str:
        return format(value, "f")


class SafeToSpendResponse(BaseModel):
    safe_to_spend: Decimal
    funding_gap: Decimal
    liquid_balance: Decimal
    committed_outflows: Decimal
    tax_reserve_shortfall: Decimal
    minimum_cash_buffer: Decimal

    @field_serializer(
        "safe_to_spend",
        "funding_gap",
        "liquid_balance",
        "committed_outflows",
        "tax_reserve_shortfall",
        "minimum_cash_buffer",
    )
    def serialize_money(self, value: Decimal) -> str:
        return format(value, "f")


class CashProjectionResponse(BaseModel):
    scenario: str
    granularity: str
    currency: str
    opening_balance: Decimal
    ending_balance: Decimal
    minimum_balance: Decimal
    first_shortfall_date: date | None
    points: list[CashProjectionPointResponse]
    safe_to_spend: SafeToSpendResponse | None = None

    @field_serializer("opening_balance", "ending_balance", "minimum_balance")
    def serialize_money(self, value: Decimal) -> str:
        return format(value, "f")

    @classmethod
    def from_result(cls, result: CashProjectionResult) -> CashProjectionResponse:
        safe = None
        if result.safe_to_spend is not None:
            s = result.safe_to_spend
            safe = SafeToSpendResponse(
                safe_to_spend=s.safe_to_spend,
                funding_gap=s.funding_gap,
                liquid_balance=s.liquid_balance,
                committed_outflows=s.committed_outflows,
                tax_reserve_shortfall=s.tax_reserve_shortfall,
                minimum_cash_buffer=s.minimum_cash_buffer,
            )
        return cls(
            scenario=result.scenario,
            granularity=result.granularity,
            currency=result.currency,
            opening_balance=result.opening_balance,
            ending_balance=result.projection.ending_balance,
            minimum_balance=result.projection.minimum_balance,
            first_shortfall_date=result.projection.first_shortfall_date,
            points=[
                CashProjectionPointResponse(
                    date=p.date,
                    inflows=p.inflows,
                    outflows=p.outflows,
                    ending_balance=p.ending_balance,
                    lowest_intraday_balance=p.lowest_intraday_balance,
                )
                for p in result.points
            ],
            safe_to_spend=safe,
        )
