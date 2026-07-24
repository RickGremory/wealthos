"""Evidence-related value objects."""

from __future__ import annotations

from wealthos.modules.tax_mx.domain.exceptions import (
    InvalidEvidenceSource,
    InvalidEvidenceStatus,
    InvalidEvidenceType,
)

EVIDENCE_STATUS = frozenset({"missing", "pending", "valid", "invalid", "mismatch"})
EVIDENCE_TYPES = frozenset({"cfdi", "bank_statement", "receipt", "contract", "manual", "other"})
EVIDENCE_SOURCES = frozenset({"manual", "import", "integration", "system"})


class EvidenceValidationStatus:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in EVIDENCE_STATUS:
            raise InvalidEvidenceStatus(f"Unsupported evidence status: {value!r}")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EvidenceValidationStatus):
            return NotImplemented
        return self._value == other._value


class TaxEvidenceType:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in EVIDENCE_TYPES:
            raise InvalidEvidenceType(f"Unsupported evidence type: {value!r}")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value


class EvidenceSource:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in EVIDENCE_SOURCES:
            raise InvalidEvidenceSource(f"Unsupported evidence source: {value!r}")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value
