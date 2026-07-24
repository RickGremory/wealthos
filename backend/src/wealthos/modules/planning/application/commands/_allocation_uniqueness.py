"""Helpers for budget allocation uniqueness checks."""

from __future__ import annotations

from wealthos.modules.planning.domain.entities.budget_allocation import BudgetAllocation
from wealthos.modules.planning.domain.exceptions import DuplicateAllocationError


def assert_unique_allocation(
    existing: list[BudgetAllocation],
    candidate: BudgetAllocation,
    *,
    exclude_id=None,
) -> None:
    for row in existing:
        if exclude_id is not None and row.id == exclude_id:
            continue
        if row.allocation_type.value != candidate.allocation_type.value:
            continue
        if _same_target(row, candidate):
            raise DuplicateAllocationError(
                "An allocation with the same type and target already exists on this budget."
            )


def _same_target(left: BudgetAllocation, right: BudgetAllocation) -> bool:
    t = left.allocation_type.value
    if t in {"income", "expense"}:
        return left.category_id == right.category_id
    if t == "goal_contribution":
        return left.goal_id == right.goal_id
    if t == "debt_payment":
        return left.debt_id == right.debt_id
    if t == "tax_reserve":
        return left.tax_profile_id == right.tax_profile_id
    if t == "savings":
        return left.destination_account_id == right.destination_account_id
    if t == "unallocated":
        return True
    return False
