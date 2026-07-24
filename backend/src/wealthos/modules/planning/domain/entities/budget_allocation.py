"""BudgetAllocation — planned amount within a budget."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.planning.domain.exceptions import (
    AllocationValidationError,
    InvalidAllocationAmount,
)
from wealthos.modules.planning.domain.value_objects.budget_allocation_type import (
    BudgetAllocationType,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(slots=True)
class BudgetAllocation:
    id: UUID
    organization_id: UUID
    budget_id: UUID
    allocation_type: BudgetAllocationType
    category_id: UUID | None
    goal_id: UUID | None
    debt_id: UUID | None
    tax_profile_id: UUID | None
    destination_account_id: UUID | None
    amount: Money
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        budget_id: UUID,
        allocation_type: str,
        amount: Money,
        category_id: UUID | None = None,
        goal_id: UUID | None = None,
        debt_id: UUID | None = None,
        tax_profile_id: UUID | None = None,
        destination_account_id: UUID | None = None,
        notes: str | None = None,
        allocation_id: UUID | None = None,
    ) -> BudgetAllocation:
        if amount.amount <= Decimal("0.00"):
            raise InvalidAllocationAmount("Allocation amount must be positive.")

        type_vo = BudgetAllocationType(allocation_type)
        allocation = cls(
            id=allocation_id or uuid4(),
            organization_id=organization_id,
            budget_id=budget_id,
            allocation_type=type_vo,
            category_id=category_id,
            goal_id=goal_id,
            debt_id=debt_id,
            tax_profile_id=tax_profile_id,
            destination_account_id=destination_account_id,
            amount=amount,
            notes=notes.strip() if notes else None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        allocation.validate_references_for_type()
        return allocation

    def validate_references_for_type(self) -> None:
        t = self.allocation_type
        if t.requires_category and self.category_id is None:
            raise AllocationValidationError(f"{t.value} allocations require category_id.")
        if t.requires_goal and self.goal_id is None:
            raise AllocationValidationError("goal_contribution allocations require goal_id.")
        if t.requires_debt and self.debt_id is None:
            raise AllocationValidationError("debt_payment allocations require debt_id.")

    def update_amount(self, amount: Money) -> None:
        if amount.amount <= Decimal("0.00"):
            raise InvalidAllocationAmount("Allocation amount must be positive.")
        if amount.currency != self.amount.currency:
            raise InvalidAllocationAmount("Allocation currency cannot change.")
        self.amount = amount
        self.updated_at = datetime.now(UTC)

    def update_notes(self, notes: str | None) -> None:
        self.notes = notes.strip() if notes else None
        self.updated_at = datetime.now(UTC)

    def update_category(self, category_id: UUID | None) -> None:
        self.category_id = category_id
        self.validate_references_for_type()
        self.updated_at = datetime.now(UTC)

    def update_goal(self, goal_id: UUID | None) -> None:
        self.goal_id = goal_id
        self.validate_references_for_type()
        self.updated_at = datetime.now(UTC)

    def update_debt(self, debt_id: UUID | None) -> None:
        self.debt_id = debt_id
        self.validate_references_for_type()
        self.updated_at = datetime.now(UTC)

    def update_tax_profile(self, tax_profile_id: UUID | None) -> None:
        self.tax_profile_id = tax_profile_id
        self.updated_at = datetime.now(UTC)

    def update_destination_account(self, destination_account_id: UUID | None) -> None:
        self.destination_account_id = destination_account_id
        self.updated_at = datetime.now(UTC)
