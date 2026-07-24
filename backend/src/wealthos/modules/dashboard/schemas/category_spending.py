"""Category spending response schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from wealthos.modules.dashboard.application.views.category_spending import (
    CategorySpendingSeriesView,
)


class CategorySpendingItemResponse(BaseModel):
    category_id: UUID
    category_name: str
    amount: Decimal
    percentage: Decimal
    transaction_count: int


class CategorySpendingSeriesResponse(BaseModel):
    currency: str
    total_expenses: Decimal
    items: list[CategorySpendingItemResponse]


class CategorySpendingResponse(BaseModel):
    """Posted expenses grouped by category (default: root category)."""

    series: list[CategorySpendingSeriesResponse]

    @classmethod
    def from_views(
        cls,
        series: list[CategorySpendingSeriesView],
    ) -> CategorySpendingResponse:
        return cls(
            series=[
                CategorySpendingSeriesResponse(
                    currency=item.currency,
                    total_expenses=item.total_expenses,
                    items=[
                        CategorySpendingItemResponse(
                            category_id=row.category_id,
                            category_name=row.category_name,
                            amount=row.amount,
                            percentage=row.percentage,
                            transaction_count=row.transaction_count,
                        )
                        for row in item.items
                    ],
                )
                for item in series
            ]
        )
