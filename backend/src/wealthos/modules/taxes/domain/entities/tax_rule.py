"""TaxRule aggregate — configurable estimation rule."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.taxes.domain.exceptions import (
    InvalidTaxRule,
    TaxRuleAlreadyArchived,
)
from wealthos.modules.taxes.domain.value_objects.calculation_method import (
    TaxCalculationMethod,
)
from wealthos.modules.taxes.domain.value_objects.percentage import Percentage
from wealthos.modules.taxes.domain.value_objects.tax_base_type import TaxBaseType
from wealthos.modules.taxes.domain.value_objects.tax_inclusion_mode import (
    TaxInclusionMode,
)
from wealthos.modules.taxes.domain.value_objects.tax_rule_name import TaxRuleName
from wealthos.modules.taxes.domain.value_objects.tax_type import TaxType
from wealthos.shared.domain.value_objects.money import Money


@dataclass(slots=True)
class TaxRule:
    id: UUID
    organization_id: UUID
    tax_profile_id: UUID
    name: TaxRuleName
    tax_type: TaxType
    calculation_method: TaxCalculationMethod
    rate: Percentage | None
    fixed_amount: Money | None
    applies_to: TaxBaseType
    tax_inclusion_mode: TaxInclusionMode
    category_ids: tuple[UUID, ...]
    priority: int
    is_active: bool
    effective_from: date
    effective_to: date | None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        tax_profile_id: UUID,
        name: str,
        tax_type: str,
        calculation_method: str,
        applies_to: str,
        effective_from: date,
        rate: Decimal | None = None,
        fixed_amount: Money | None = None,
        tax_inclusion_mode: str = "exclusive",
        category_ids: tuple[UUID, ...] | list[UUID] = (),
        priority: int = 100,
        effective_to: date | None = None,
        rule_id: UUID | None = None,
    ) -> TaxRule:
        method = TaxCalculationMethod(calculation_method)
        rate_vo = Percentage(rate) if rate is not None else None
        if method.value == "percentage":
            if rate_vo is None:
                raise InvalidTaxRule("percentage method requires rate.")
            if fixed_amount is not None:
                raise InvalidTaxRule("percentage method cannot include fixed_amount.")
        else:
            if fixed_amount is None:
                raise InvalidTaxRule("fixed method requires fixed_amount.")
            if rate_vo is not None:
                raise InvalidTaxRule("fixed method cannot include rate.")
            if fixed_amount.amount <= 0:
                raise InvalidTaxRule("fixed_amount must be positive.")
        if effective_to is not None and effective_to < effective_from:
            raise InvalidTaxRule("effective_to cannot be before effective_from.")

        now = datetime.now(UTC)
        return cls(
            id=rule_id or uuid4(),
            organization_id=organization_id,
            tax_profile_id=tax_profile_id,
            name=TaxRuleName(name),
            tax_type=TaxType(tax_type),
            calculation_method=method,
            rate=rate_vo,
            fixed_amount=fixed_amount,
            applies_to=TaxBaseType(applies_to),
            tax_inclusion_mode=TaxInclusionMode(tax_inclusion_mode),
            category_ids=tuple(dict.fromkeys(category_ids)),
            priority=priority,
            is_active=True,
            effective_from=effective_from,
            effective_to=effective_to,
            created_at=now,
            updated_at=now,
            archived_at=None,
        )

    def is_effective_on(self, on_date: date) -> bool:
        if on_date < self.effective_from:
            return False
        if self.effective_to is not None and on_date > self.effective_to:
            return False
        return self.is_active and self.archived_at is None

    def archive(self) -> None:
        if self.archived_at is not None:
            raise TaxRuleAlreadyArchived("Tax rule is already archived.")
        now = datetime.now(UTC)
        self.is_active = False
        self.archived_at = now
        self.updated_at = now

    def rename(self, name: str) -> None:
        self._ensure_mutable()
        self.name = TaxRuleName(name)
        self.updated_at = datetime.now(UTC)

    def change_rate(self, rate: Decimal) -> None:
        self._ensure_mutable()
        if self.calculation_method.value != "percentage":
            raise InvalidTaxRule("Only percentage rules have a rate.")
        self.rate = Percentage(rate)
        self.updated_at = datetime.now(UTC)

    def change_fixed_amount(self, amount: Money) -> None:
        self._ensure_mutable()
        if self.calculation_method.value != "fixed":
            raise InvalidTaxRule("Only fixed rules have a fixed_amount.")
        if amount.amount <= 0:
            raise InvalidTaxRule("fixed_amount must be positive.")
        self.fixed_amount = amount
        self.updated_at = datetime.now(UTC)

    def change_priority(self, priority: int) -> None:
        self._ensure_mutable()
        self.priority = priority
        self.updated_at = datetime.now(UTC)

    def change_effective_window(
        self,
        *,
        effective_from: date | None = None,
        effective_to: date | None = None,
        clear_effective_to: bool = False,
    ) -> None:
        self._ensure_mutable()
        start = effective_from if effective_from is not None else self.effective_from
        end = (
            None
            if clear_effective_to
            else (effective_to if effective_to is not None else self.effective_to)
        )
        if end is not None and end < start:
            raise InvalidTaxRule("effective_to cannot be before effective_from.")
        self.effective_from = start
        self.effective_to = end
        self.updated_at = datetime.now(UTC)

    def replace_categories(self, category_ids: tuple[UUID, ...] | list[UUID]) -> None:
        self._ensure_mutable()
        self.category_ids = tuple(dict.fromkeys(category_ids))
        self.updated_at = datetime.now(UTC)

    def _ensure_mutable(self) -> None:
        if self.archived_at is not None:
            raise TaxRuleAlreadyArchived("Cannot update an archived tax rule.")
