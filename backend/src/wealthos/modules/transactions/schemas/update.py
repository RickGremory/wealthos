"""Transaction update schema."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TransactionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    description: str | None = Field(default=None, min_length=2, max_length=200)
    notes: str | None = None
    occurred_at: datetime | None = None
    category_id: UUID | None = None

    @model_validator(mode="after")
    def reject_empty_payload(self) -> TransactionUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self
