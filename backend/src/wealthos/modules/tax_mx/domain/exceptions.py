"""Domain errors for the tax_mx module."""


class TaxMxError(Exception):
    """Base domain error for Mexican tax specialization."""


class InvalidRFC(TaxMxError):
    pass


class InvalidMexicoPersonType(TaxMxError):
    pass


class InvalidMexicoIncomeTreatment(TaxMxError):
    pass


class InvalidMexicoExpenseTreatment(TaxMxError):
    pass


class InvalidMexicoVATTreatment(TaxMxError):
    pass


class InvalidEvidenceStatus(TaxMxError):
    pass


class InvalidEvidenceType(TaxMxError):
    pass


class InvalidEvidenceSource(TaxMxError):
    pass


class InvalidWithholdingType(TaxMxError):
    pass


class InvalidTaxDetails(TaxMxError):
    pass


class InvalidMexicoTaxConfiguration(TaxMxError):
    pass


class MexicoTaxConfigurationNotFound(TaxMxError):
    pass


class MexicoTaxConfigurationOverlap(TaxMxError):
    pass


class MexicoTaxRegimeInvalid(TaxMxError):
    pass


class MexicoTaxProfileRequired(TaxMxError):
    pass


class MexicoTaxProfileIncompatible(TaxMxError):
    pass


class MexicoClassificationNotFound(TaxMxError):
    pass


class MexicoTaxPeriodClosed(TaxMxError):
    pass


class MexicoTaxPeriodNotFound(TaxMxError):
    pass


class MexicoCatalogNotFound(TaxMxError):
    pass


class MexicoTransactionNotFound(TaxMxError):
    pass


class MexicoCategoryNotFound(TaxMxError):
    pass


class MexicoTaxDetailsNotFound(TaxMxError):
    pass


class CashFlowBasisRequired(TaxMxError):
    pass
