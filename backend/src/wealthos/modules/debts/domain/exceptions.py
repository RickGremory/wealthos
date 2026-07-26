"""Domain errors for the debts module."""


class DebtError(Exception):
    """Base domain error for debts."""


class DebtNameEmpty(DebtError):
    """Raised when a debt name is blank or too short."""


class DebtNameTooLong(DebtError):
    """Raised when a debt name exceeds the allowed length."""


class InvalidDebtType(DebtError):
    """Raised when a debt type is not supported."""


class InvalidDebtStatus(DebtError):
    """Raised when a debt status is not supported."""


class InvalidDebtPriority(DebtError):
    """Raised when a debt priority is not supported."""


class InvalidInterestRate(DebtError):
    """Raised when an interest rate is invalid."""


class InvalidPaymentAmount(DebtError):
    """Raised when a payment amount field is invalid (negative, currency, etc.)."""


class InvalidCalendarDay(DebtError):
    """Raised when due_day or statement_day is out of range."""


class DebtNotFoundError(DebtError):
    """Raised when a debt cannot be found in the organization."""


class DebtAlreadyArchived(DebtError):
    """Raised when operating on an archived debt."""


class DebtAlreadyClosed(DebtError):
    """Raised when a debt product is already closed."""


class DebtAlreadyPaused(DebtError):
    """Raised when pausing an already paused debt."""


class DebtNotPaused(DebtError):
    """Raised when resuming a debt that is not paused."""


class DebtAccountNotFound(DebtError):
    """Raised when the linked account is missing."""


class DebtAccountMustBeLiability(DebtError):
    """Raised when linking a non-liability account."""


class DebtAccountInactive(DebtError):
    """Raised when linking an archived account."""


class DebtCurrencyMismatch(DebtError):
    """Raised when debt currency does not match the account."""


class DebtAlreadyExistsForAccount(DebtError):
    """Raised when a debt already exists for the account (1:1)."""


class DebtPaymentExceedsBalance(DebtError):
    """Raised when a payment would make the liability balance positive."""


class DebtPaymentAmountInvalid(DebtError):
    """Raised when payment amount is not positive."""


class DebtPaymentBreakdownInvalid(DebtError):
    """Raised when principal + interest does not equal amount."""


class DebtPaymentSourceInvalid(DebtError):
    """Raised when the source account cannot fund the payment."""


class CannotUpdateDebtField(DebtError):
    """Raised when attempting to change an immutable debt field."""


class InvalidPayoffStrategy(DebtError):
    """Raised when payoff strategy is not supported."""


# Backward-compatible aliases during SPEC-002 convergence
InvalidMinimumPayment = InvalidPaymentAmount
InvalidPaymentDay = InvalidCalendarDay
DebtAlreadyPaidOff = DebtAlreadyClosed
