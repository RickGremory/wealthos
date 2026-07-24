"""RecordTaxPayment command."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.categories.domain.value_objects.category_type import CategoryType
from wealthos.modules.taxes.application.services.financial_expense_service import (
    FinancialExpenseService,
)
from wealthos.modules.taxes.domain.entities.tax_payment import TaxPayment
from wealthos.modules.taxes.domain.exceptions import (
    TaxCategoryNotFound,
    TaxPaymentSourceInvalid,
    TaxPeriodNotFound,
)
from wealthos.modules.taxes.domain.repositories.tax_payment_repository import (
    TaxPaymentRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_period_repository import (
    TaxPeriodRepository,
)
from wealthos.shared.domain.value_objects.money import Money

TAX_EXPENSE_CATEGORY_NAME = "Impuestos"


@dataclass(frozen=True, slots=True)
class RecordTaxPaymentInput:
    organization_id: UUID
    tax_period_id: UUID
    source_account_id: UUID
    amount: Decimal
    tax_type: str
    paid_at: datetime
    created_by_user_id: UUID
    reference: str | None = None
    notes: str | None = None
    idempotency_key: str | None = None


class RecordTaxPaymentCommand:
    def __init__(
        self,
        periods: TaxPeriodRepository,
        payments: TaxPaymentRepository,
        accounts: AccountRepository,
        categories: CategoryRepository,
        expenses: FinancialExpenseService,
    ) -> None:
        self._periods = periods
        self._payments = payments
        self._accounts = accounts
        self._categories = categories
        self._expenses = expenses

    def execute(self, data: RecordTaxPaymentInput) -> TaxPayment:
        if data.idempotency_key:
            existing = self._payments.get_by_idempotency_key(
                data.organization_id,
                data.idempotency_key,
            )
            if existing is not None:
                return existing

        period = self._periods.get_by_id(data.organization_id, data.tax_period_id)
        if period is None:
            raise TaxPeriodNotFound("Tax period not found.")

        account = self._accounts.get_by_id(data.organization_id, data.source_account_id)
        if account is None or not account.is_active:
            raise TaxPaymentSourceInvalid("Source account not found or inactive.")
        if not account.account_type.is_asset:
            raise TaxPaymentSourceInvalid("Source account must be an asset account.")
        if account.currency.value != period.currency.value:
            raise TaxPaymentSourceInvalid("Source account currency must match period currency.")

        category_id = self._resolve_tax_category(data.organization_id)
        amount = Money(data.amount, period.currency.value)
        description = data.reference or f"Tax payment: {data.tax_type}"

        transaction_id = self._expenses.create_expense(
            organization_id=data.organization_id,
            account_id=data.source_account_id,
            category_id=category_id,
            amount=amount,
            description=description,
            occurred_at=data.paid_at,
            created_by_user_id=data.created_by_user_id,
            notes=data.notes,
        )

        payment = TaxPayment.create(
            organization_id=data.organization_id,
            tax_period_id=data.tax_period_id,
            tax_type=data.tax_type,
            transaction_id=transaction_id,
            source_account_id=data.source_account_id,
            amount=amount,
            paid_at=data.paid_at,
            created_by_user_id=data.created_by_user_id,
            reference=data.reference,
            notes=data.notes,
            idempotency_key=data.idempotency_key,
        )
        return self._payments.add(payment)

    def _resolve_tax_category(self, organization_id: UUID) -> UUID:
        categories = self._categories.list_by_organization(
            organization_id,
            category_type=CategoryType("expense"),
        )
        match = next(
            (
                category
                for category in categories
                if category.name.value == TAX_EXPENSE_CATEGORY_NAME
            ),
            None,
        )
        if match is None:
            raise TaxCategoryNotFound(
                f'Expense category "{TAX_EXPENSE_CATEGORY_NAME}" not found for organization.'
            )
        return match.id
