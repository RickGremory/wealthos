"""Tax summary and reserve recommendation schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from wealthos.modules.taxes.application.queries.get_tax_reserve_recommendation import (
    TaxReserveRecommendation,
)
from wealthos.modules.taxes.application.queries.get_tax_summary import TaxSummary


class TaxSummaryByCurrencyResponse(BaseModel):
    currency: str
    estimated_tax: Decimal
    paid: Decimal
    balance: Decimal = Field(description="estimated_tax minus paid")
    reserve_balance: Decimal
    cash_like_assets: Decimal
    available_after_tax: Decimal = Field(
        description="Cash-like assets minus unpaid estimated tax",
    )


class TaxSummaryResponse(BaseModel):
    """Operational tax estimates — not formal tax advice."""

    has_active_profile: bool
    current_period_id: UUID | None
    by_currency: list[TaxSummaryByCurrencyResponse]

    @classmethod
    def from_summary(cls, summary: TaxSummary) -> TaxSummaryResponse:
        return cls(
            has_active_profile=summary.has_active_profile,
            current_period_id=summary.current_period_id,
            by_currency=[
                TaxSummaryByCurrencyResponse(
                    currency=item.currency,
                    estimated_tax=item.estimated_tax,
                    paid=item.paid,
                    balance=item.balance,
                    reserve_balance=item.reserve_balance,
                    cash_like_assets=item.cash_like_assets,
                    available_after_tax=item.available_after_tax,
                )
                for item in summary.by_currency
            ],
        )


class TaxReserveRecommendationResponse(BaseModel):
    currency: str
    estimated_tax: Decimal
    paid: Decimal
    reserve_balance: Decimal
    recommended_transfer: Decimal = Field(
        description="max(estimated_tax - paid - reserve_balance, 0)",
    )

    @classmethod
    def from_item(cls, item: TaxReserveRecommendation) -> TaxReserveRecommendationResponse:
        return cls(
            currency=item.currency,
            estimated_tax=item.estimated_tax,
            paid=item.paid,
            reserve_balance=item.reserve_balance,
            recommended_transfer=item.recommended_transfer,
        )


class TaxReserveRecommendationListResponse(BaseModel):
    items: list[TaxReserveRecommendationResponse]

    @classmethod
    def from_items(
        cls,
        items: list[TaxReserveRecommendation],
    ) -> TaxReserveRecommendationListResponse:
        return cls(items=[TaxReserveRecommendationResponse.from_item(item) for item in items])
