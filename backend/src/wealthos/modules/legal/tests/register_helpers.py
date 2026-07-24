"""Shared legal acceptance payload for API integration tests."""

from __future__ import annotations

DEFAULT_LEGAL_ACCEPTANCES = [
    {
        "document_type": "terms_of_service",
        "version": "1.0",
        "accepted": True,
    },
    {
        "document_type": "privacy_notice",
        "version": "1.0",
        "acknowledged": True,
    },
]


def register_json(**overrides: object) -> dict:
    """Build a valid registration JSON body including legal acceptances."""
    payload: dict = {
        "email": "user@example.com",
        "password": "WealthOS-2026-Segura",
        "display_name": "Test User",
        "organization_name": "Test Org",
        "legal_acceptances": list(DEFAULT_LEGAL_ACCEPTANCES),
        "marketing_consent": False,
    }
    payload.update(overrides)
    return payload
