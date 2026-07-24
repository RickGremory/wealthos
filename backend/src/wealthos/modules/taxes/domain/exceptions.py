"""Domain errors for the taxes module."""


class TaxError(Exception):
    """Base domain error for taxes."""


class TaxProfileNotFound(TaxError):
    pass


class TaxProfileAlreadyActive(TaxError):
    pass


class InvalidCountryCode(TaxError):
    pass


class InvalidTaxpayerType(TaxError):
    pass


class InvalidFilingFrequency(TaxError):
    pass


class InvalidFiscalYearStartMonth(TaxError):
    pass


class InvalidTaxType(TaxError):
    pass


class InvalidCalculationMethod(TaxError):
    pass


class InvalidTaxBaseType(TaxError):
    pass


class InvalidTaxTreatment(TaxError):
    pass


class InvalidTaxInclusionMode(TaxError):
    pass


class InvalidTaxRule(TaxError):
    pass


class TaxRuleNameEmpty(TaxError):
    pass


class TaxRuleNameTooLong(TaxError):
    pass


class TaxRuleNotFound(TaxError):
    pass


class TaxRuleAlreadyArchived(TaxError):
    pass


class TaxPeriodNotFound(TaxError):
    pass


class TaxPeriodClosed(TaxError):
    pass


class TaxPeriodNotCalculated(TaxError):
    pass


class TaxPeriodAlreadyClosed(TaxError):
    pass


class InvalidTaxPeriod(TaxError):
    pass


class TaxReserveAccountInvalid(TaxError):
    pass


class TaxPaymentAmountInvalid(TaxError):
    pass


class TaxPaymentSourceInvalid(TaxError):
    pass


class TaxCategoryNotFound(TaxError):
    pass


class TaxTransactionNotFound(TaxError):
    pass


class DuplicateIdempotencyKey(TaxError):
    pass


class InvalidDeductibilityPercentage(TaxError):
    pass


class InvalidPercentage(TaxError):
    pass
