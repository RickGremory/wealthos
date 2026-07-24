"""Domain errors for the goals module."""


class GoalError(Exception):
    """Base domain error for goals."""


class GoalNameEmpty(GoalError):
    """Raised when a goal name is blank or too short."""


class GoalNameTooLong(GoalError):
    """Raised when a goal name exceeds the allowed length."""


class InvalidGoalStatus(GoalError):
    """Raised when a goal status is not supported."""


class InvalidGoalStrategy(GoalError):
    """Raised when a goal strategy is not supported."""


class InvalidTargetAmount(GoalError):
    """Raised when target amount is not positive."""


class GoalNotFoundError(GoalError):
    """Raised when a goal cannot be found in the organization."""


class GoalAlreadyArchived(GoalError):
    """Raised when archiving an already archived goal."""


class GoalAlreadyCompleted(GoalError):
    """Raised when completing an already completed goal."""


class StrategyDoesNotSupportManualProgress(GoalError):
    """Raised when updating manual progress on a non-manual goal."""


class LinkedAccountsRequired(GoalError):
    """Raised when linked_accounts strategy has no accounts."""


class LinkedAccountsNotAllowed(GoalError):
    """Raised when linked accounts are provided for a non-linked strategy."""


class GoalAccountCurrencyMismatch(GoalError):
    """Raised when a linked account currency differs from the goal currency."""


class GoalAccountNotFound(GoalError):
    """Raised when a linked account is missing in the organization."""


class GoalAccountInactive(GoalError):
    """Raised when linking an archived account."""


class CannotChangeGoalStrategy(GoalError):
    """Raised when attempting to change strategy after creation."""
