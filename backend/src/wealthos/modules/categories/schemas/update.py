"""Category update schema."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=80)
    icon: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, max_length=20)

    @model_validator(mode="after")
    def reject_empty_payload(self) -> CategoryUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self
