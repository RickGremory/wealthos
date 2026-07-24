"""Map planning domain exceptions to HTTP errors."""

from __future__ import annotations

from fastapi import HTTPException, status

from wealthos.modules.planning.domain.exceptions import (
    AllocationValidationError,
    BudgetAllocationNotFoundError,
    BudgetAlreadyArchived,
    BudgetClosed,
    BudgetNameEmpty,
    BudgetNameTooLong,
    BudgetNotEditable,
    BudgetNotFoundError,
    CashPlanAlreadyArchived,
    CashPlanItemNotFoundError,
    CashPlanItemNotMatchable,
    CashPlanNameEmpty,
    CashPlanNameTooLong,
    CashPlanNotFoundError,
    ConcurrentMatchConflict,
    CurrencyMismatchError,
    DuplicateAllocationError,
    InvalidAllocationAmount,
    InvalidBudgetAllocationType,
    InvalidBudgetDateRange,
    InvalidBudgetPeriodType,
    InvalidBudgetStatus,
    InvalidCashBufferType,
    InvalidCashPlanDateRange,
    InvalidCashPlanItemAmount,
    InvalidCashPlanItemStatus,
    InvalidCashPlanItemType,
    InvalidCashPlanStatus,
    InvalidCashScenario,
    InvalidForecastMethod,
    InvalidLinkedEntityType,
    InvalidOpeningBalanceMode,
    InvalidPercentage,
    InvalidProbability,
    InvalidRolloverPolicy,
    LinkedResourceCurrencyMismatch,
    LinkedResourceNotFound,
    MatchAmountExceedsRemaining,
    MatchTransactionInvalid,
    OpeningBalanceInvalid,
    PlanningError,
    SelectedAccountsRequired,
)
from wealthos.shared.domain.exceptions import InvalidCurrency


def http_map_planning_errors(exc: Exception) -> HTTPException:
    if isinstance(
        exc,
        (
            BudgetNotFoundError,
            CashPlanNotFoundError,
            BudgetAllocationNotFoundError,
            CashPlanItemNotFoundError,
            LinkedResourceNotFound,
        ),
    ):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    if isinstance(
        exc,
        (
            BudgetNameEmpty,
            BudgetNameTooLong,
            CashPlanNameEmpty,
            CashPlanNameTooLong,
            InvalidBudgetPeriodType,
            InvalidBudgetStatus,
            InvalidRolloverPolicy,
            InvalidForecastMethod,
            InvalidBudgetAllocationType,
            InvalidCashPlanStatus,
            InvalidOpeningBalanceMode,
            InvalidCashBufferType,
            InvalidCashPlanItemType,
            InvalidCashPlanItemStatus,
            InvalidLinkedEntityType,
            InvalidCashScenario,
            InvalidPercentage,
            InvalidProbability,
            InvalidBudgetDateRange,
            InvalidCashPlanDateRange,
            InvalidAllocationAmount,
            InvalidCashPlanItemAmount,
            InvalidCurrency,
        ),
    ):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    if isinstance(
        exc,
        (
            BudgetAlreadyArchived,
            CashPlanAlreadyArchived,
            DuplicateAllocationError,
            ConcurrentMatchConflict,
        ),
    ):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    if isinstance(
        exc,
        (
            BudgetClosed,
            BudgetNotEditable,
            AllocationValidationError,
            CurrencyMismatchError,
            LinkedResourceCurrencyMismatch,
            OpeningBalanceInvalid,
            SelectedAccountsRequired,
            MatchAmountExceedsRemaining,
            MatchTransactionInvalid,
            CashPlanItemNotMatchable,
        ),
    ):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if isinstance(exc, PlanningError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
