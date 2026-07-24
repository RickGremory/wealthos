"""Pydantic schemas for the legal API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RegistrationDocumentRequirement(BaseModel):
    type: str
    version: str
    title: str
    url: str
    acceptance_required: bool | None = None
    acknowledgement_required: bool | None = None


class MarketingConsentAvailability(BaseModel):
    available: bool
    required: bool


class RegistrationRequirementsResponse(BaseModel):
    documents: list[RegistrationDocumentRequirement]
    marketing_consent: MarketingConsentAvailability


class LegalDocumentResponse(BaseModel):
    type: str
    version: str
    title: str
    url: str
    content_markdown: str
    effective_at: datetime
    published_at: datetime
    requires_reacceptance: bool
    change_summary: str | None = None


class PendingDocumentResponse(BaseModel):
    type: str
    version: str
    title: str
    url: str


class ComplianceStatusResponse(BaseModel):
    is_compliant: bool
    pending_documents: list[PendingDocumentResponse]


class LegalAcceptanceRequestItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_type: str = Field(min_length=1, max_length=40)
    version: str = Field(min_length=1, max_length=20)
    accepted: bool | None = None
    acknowledged: bool | None = None


class AcceptDocumentsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    acceptances: list[LegalAcceptanceRequestItem] = Field(min_length=1)


class UserDocumentItem(BaseModel):
    type: str
    version: str
    title: str
    url: str
    accepted_at: datetime
    consent_type: str


class MarketingConsentState(BaseModel):
    opted_in: bool
    updated_at: datetime | None = None


class UserDocumentsResponse(BaseModel):
    documents: list[UserDocumentItem]
    marketing_consent: MarketingConsentState


class MarketingConsentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accepted: bool
