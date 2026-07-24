"""Category collection schemas."""

from __future__ import annotations

from pydantic import BaseModel

from wealthos.modules.categories.schemas.response import (
    CategoryResponse,
    CategoryTreeItem,
)


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    total: int


class CategoryTreeResponse(BaseModel):
    items: list[CategoryTreeItem]
    total: int
