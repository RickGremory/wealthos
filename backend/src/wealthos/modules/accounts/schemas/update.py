"""Account update schema."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AccountUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=100)
    institution_name: str | None = Field(default=None, max_length=120)
    last_four: str | None = Field(default=None, min_length=4, max_length=4)

    @model_validator(mode="after")
    def reject_empty_payload(self) -> AccountUpdate:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self
