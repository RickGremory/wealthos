"""Auth request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LegalAcceptancePayload(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    document_type: str = Field(min_length=1, max_length=40)
    version: str = Field(min_length=1, max_length=20)
    accepted: bool | None = None
    acknowledged: bool | None = None


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=100)
    organization_name: str = Field(min_length=1, max_length=120)
    currency: str = Field(default="MXN", min_length=3, max_length=3)
    timezone: str = Field(default="America/Cancun", max_length=64)
    locale: str = Field(default="es-MX", min_length=5, max_length=16)
    legal_acceptances: list[LegalAcceptancePayload] = Field(default_factory=list)
    marketing_consent: bool = False


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
