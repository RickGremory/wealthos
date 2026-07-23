"""Request schema for creating an organization."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreate(BaseModel):
    """HTTP body for POST /organizations."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        examples=["ricardo-personal"],
    )
    currency: str = Field(default="MXN", min_length=3, max_length=3)
    timezone: str = Field(default="America/Mexico_City", max_length=64)
    locale: str = Field(default="es_MX", min_length=5, max_length=5)
