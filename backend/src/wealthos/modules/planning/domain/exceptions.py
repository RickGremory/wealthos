"""Domain errors for the planning module."""


class PlanningError(Exception):
    """Base domain error for planning."""


class BudgetNameEmpty(PlanningError):
    """Raised when a budget name is blank or too short."""


class BudgetNameTooLong(PlanningError):
    """Raised when a budget name exceeds the allowed length."""


class CashPlanNameEmpty(PlanningError):
    """Raised when a cash plan name is blank or too short."""


class CashPlanNameTooLong(PlanningError):
    """Raised when a cash plan name exceeds the allowed length."""


class InvalidBudgetPeriodType(PlanningError):
    """Raised when a budget period type is not supported."""


class InvalidBudgetStatus(PlanningError):
    """Raised when a budget status is not supported."""


class InvalidRolloverPolicy(PlanningError):
    """Raised when a rollover policy is not supported."""


class InvalidForecastMethod(PlanningError):
    """Raised when a forecast method is not supported."""


class InvalidBudgetAllocationType(PlanningError):
    """Raised when a budget allocation type is not supported."""


class InvalidCashPlanStatus(PlanningError):
    """Raised when a cash plan status is not supported."""


class InvalidOpeningBalanceMode(PlanningError):
    """Raised when an opening balance mode is not supported."""


class InvalidCashBufferType(PlanningError):
    """Raised when a cash buffer type is not supported."""


class InvalidCashPlanItemType(PlanningError):
    """Raised when a cash plan item type is not supported."""


class InvalidCashPlanItemStatus(PlanningError):
    """Raised when a cash plan item status is not supported."""


class InvalidLinkedEntityType(PlanningError):
    """Raised when a linked entity type is not supported."""


class InvalidCashScenario(PlanningError):
    """Raised when a cash scenario is not supported."""


class InvalidPercentage(PlanningError):
    """Raised when a percentage value is invalid."""


class InvalidBudgetDateRange(PlanningError):
    """Raised when budget dates are invalid."""


class InvalidCashPlanDateRange(PlanningError):
    """Raised when cash plan dates are invalid."""


class InvalidAllocationAmount(PlanningError):
    """Raised when an allocation amount is not positive."""


class InvalidCashPlanItemAmount(PlanningError):
    """Raised when a cash plan item amount is not positive."""


class InvalidProbability(PlanningError):
    """Raised when a probability is outside 0–100."""


class BudgetNotFoundError(PlanningError):
    """Raised when a budget cannot be found in the organization."""


class CashPlanNotFoundError(PlanningError):
    """Raised when a cash plan cannot be found in the organization."""


class BudgetAllocationNotFoundError(PlanningError):
    """Raised when a budget allocation cannot be found."""


class CashPlanItemNotFoundError(PlanningError):
    """Raised when a cash plan item cannot be found."""


class BudgetNotEditable(PlanningError):
    """Raised when the budget cannot be edited in its current status."""


class BudgetClosed(PlanningError):
    """Raised when operating on a closed budget."""


class BudgetAlreadyArchived(PlanningError):
    """Raised when operating on an archived budget."""


class CashPlanAlreadyArchived(PlanningError):
    """Raised when operating on an archived cash plan."""


class AllocationValidationError(PlanningError):
    """Raised when allocation references do not match the allocation type."""


class CurrencyMismatchError(PlanningError):
    """Raised when currencies do not match within planning aggregates."""


class LinkedResourceNotFound(PlanningError):
    """Raised when a linked goal, debt, account, or category is missing."""


class LinkedResourceCurrencyMismatch(PlanningError):
    """Raised when a linked resource uses an incompatible currency."""


class DuplicateAllocationError(PlanningError):
    """Raised when a duplicate allocation already exists for the budget."""


class OpeningBalanceInvalid(PlanningError):
    """Raised when opening balance configuration is invalid."""


class SelectedAccountsRequired(PlanningError):
    """Raised when selected_accounts mode has no accounts."""


class MatchAmountExceedsRemaining(PlanningError):
    """Raised when a match amount exceeds the remaining planned amount."""


class MatchTransactionInvalid(PlanningError):
    """Raised when a transaction cannot be matched to a planning item."""


class CashPlanItemNotMatchable(PlanningError):
    """Raised when a cash plan item cannot accept matches."""


class ConcurrentMatchConflict(PlanningError):
    """Raised when concurrent matches conflict on remaining amount."""
