"""Category create schema."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=80)
    category_type: Literal["income", "expense"]
    parent_id: UUID | None = None
    icon: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, max_length=20)
