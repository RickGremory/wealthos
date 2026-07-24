"""Withholding type and income-tax estimation enums."""

from __future__ import annotations

from wealthos.modules.tax_mx.domain.exceptions import InvalidMexicoTaxConfiguration

WITHHOLDING_TYPES = frozenset({"income_tax", "vat", "other"})
INCOME_TAX_METHODS = frozenset({"configured_rate"})
INCOME_TAX_BASES = frozenset({"gross_taxable_income", "net_taxable_income"})
CALCULATION_SOURCES = frozenset({"manual", "derived", "cfdi", "imported"})


class MexicoWithholdingType:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in WITHHOLDING_TYPES:
            raise InvalidMexicoTaxConfiguration(f"Unsupported withholding type: {value!r}")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value


class IncomeTaxEstimationMethod:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in INCOME_TAX_METHODS:
            raise InvalidMexicoTaxConfiguration(
                f"Unsupported income tax estimation method: {value!r}"
            )
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value


class IncomeTaxEstimationBase:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in INCOME_TAX_BASES:
            raise InvalidMexicoTaxConfiguration(
                f"Unsupported income tax estimation base: {value!r}"
            )
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value


class TaxDetailCalculationSource:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = value.strip().lower()
        if cleaned not in CALCULATION_SOURCES:
            raise InvalidMexicoTaxConfiguration(f"Unsupported calculation source: {value!r}")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value
