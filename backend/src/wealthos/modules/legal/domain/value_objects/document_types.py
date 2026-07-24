"""Legal document type and consent type constants."""

from __future__ import annotations

DOCUMENT_TERMS = "terms_of_service"
DOCUMENT_PRIVACY = "privacy_notice"
DOCUMENT_COOKIES = "cookie_policy"

CONSENT_TERMS = "terms_acceptance"
CONSENT_PRIVACY = "privacy_acknowledgement"
CONSENT_MARKETING = "marketing_opt_in"

SOURCE_REGISTRATION = "registration"
SOURCE_SETTINGS = "settings"
SOURCE_FORCED_REACCEPTANCE = "forced_reacceptance"

# Documents that must be accepted/acknowledged at registration.
REQUIRED_REGISTRATION_TYPES = (DOCUMENT_TERMS, DOCUMENT_PRIVACY)

CONSENT_TYPE_BY_DOCUMENT = {
    DOCUMENT_TERMS: CONSENT_TERMS,
    DOCUMENT_PRIVACY: CONSENT_PRIVACY,
}
