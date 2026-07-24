"""FastAPI dependencies for the taxes module."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.accounts.infrastructure.repositories import (
    SqlAlchemyAccountRepository,
)
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.categories.infrastructure.repositories import (
    SqlAlchemyCategoryRepository,
)
from wealthos.modules.taxes.application.commands.archive_tax_rule import ArchiveTaxRuleCommand
from wealthos.modules.taxes.application.commands.calculate_tax_period import (
    CalculateTaxPeriodCommand,
)
from wealthos.modules.taxes.application.commands.close_tax_period import CloseTaxPeriodCommand
from wealthos.modules.taxes.application.commands.create_tax_profile import (
    CreateTaxProfileCommand,
)
from wealthos.modules.taxes.application.commands.create_tax_rule import CreateTaxRuleCommand
from wealthos.modules.taxes.application.commands.map_tax_category import MapTaxCategoryCommand
from wealthos.modules.taxes.application.commands.override_transaction_tax_treatment import (
    OverrideTransactionTaxTreatmentCommand,
)
from wealthos.modules.taxes.application.commands.record_tax_payment import (
    RecordTaxPaymentCommand,
)
from wealthos.modules.taxes.application.commands.update_tax_profile import (
    UpdateTaxProfileCommand,
)
from wealthos.modules.taxes.application.commands.update_tax_rule import UpdateTaxRuleCommand
from wealthos.modules.taxes.application.queries.get_tax_period import GetTaxPeriodQuery
from wealthos.modules.taxes.application.queries.get_tax_profile import GetTaxProfileQuery
from wealthos.modules.taxes.application.queries.get_tax_reserve_recommendation import (
    GetTaxReserveRecommendationQuery,
)
from wealthos.modules.taxes.application.queries.get_tax_summary import GetTaxSummaryQuery
from wealthos.modules.taxes.application.queries.list_tax_periods import ListTaxPeriodsQuery
from wealthos.modules.taxes.application.queries.list_tax_profiles import ListTaxProfilesQuery
from wealthos.modules.taxes.application.queries.list_tax_rules import ListTaxRulesQuery
from wealthos.modules.taxes.application.services.financial_expense_service import (
    CreateExpenseFinancialExpenseService,
    FinancialExpenseService,
)
from wealthos.modules.taxes.application.services.tax_calculation_service import (
    TaxCalculationService,
)
from wealthos.modules.taxes.application.services.tax_period_generator import (
    TaxPeriodGenerator,
)
from wealthos.modules.taxes.domain.repositories.tax_calculation_repository import (
    TaxCalculationRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_category_mapping_repository import (
    TaxCategoryMappingRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_payment_repository import (
    TaxPaymentRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_period_repository import (
    TaxPeriodRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_read_repository import TaxReadRepository
from wealthos.modules.taxes.domain.repositories.tax_rule_repository import TaxRuleRepository
from wealthos.modules.taxes.domain.repositories.tax_transaction_override_repository import (
    TaxTransactionOverrideRepository,
)
from wealthos.modules.taxes.infrastructure.repositories import (
    SqlAlchemyTaxCalculationRepository,
    SqlAlchemyTaxCategoryMappingRepository,
    SqlAlchemyTaxPaymentRepository,
    SqlAlchemyTaxPeriodRepository,
    SqlAlchemyTaxProfileRepository,
    SqlAlchemyTaxReadRepository,
    SqlAlchemyTaxRuleRepository,
    SqlAlchemyTaxTransactionOverrideRepository,
)
from wealthos.modules.transactions.application.commands.create_expense import (
    CreateExpenseCommand,
)
from wealthos.modules.transactions.application.services.transaction_posting_service import (
    TransactionPostingService,
)
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionRepository,
)
from wealthos.modules.transactions.infrastructure.repositories import (
    SqlAlchemyTransactionRepository,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


def get_unit_of_work(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_tax_profile_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TaxProfileRepository:
    return SqlAlchemyTaxProfileRepository(session)


def get_tax_rule_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TaxRuleRepository:
    return SqlAlchemyTaxRuleRepository(session)


def get_tax_period_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TaxPeriodRepository:
    return SqlAlchemyTaxPeriodRepository(session)


def get_tax_calculation_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TaxCalculationRepository:
    return SqlAlchemyTaxCalculationRepository(session)


def get_tax_payment_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TaxPaymentRepository:
    return SqlAlchemyTaxPaymentRepository(session)


def get_tax_read_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TaxReadRepository:
    return SqlAlchemyTaxReadRepository(session)


def get_tax_category_mapping_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TaxCategoryMappingRepository:
    return SqlAlchemyTaxCategoryMappingRepository(session)


def get_tax_transaction_override_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TaxTransactionOverrideRepository:
    return SqlAlchemyTaxTransactionOverrideRepository(session)


def get_account_repository(
    session: Annotated[Session, Depends(get_db)],
) -> AccountRepository:
    return SqlAlchemyAccountRepository(session)


def get_category_repository(
    session: Annotated[Session, Depends(get_db)],
) -> CategoryRepository:
    return SqlAlchemyCategoryRepository(session)


def get_transaction_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TransactionRepository:
    return SqlAlchemyTransactionRepository(session)


def get_posting_service(
    transactions: Annotated[TransactionRepository, Depends(get_transaction_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    categories: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> TransactionPostingService:
    return TransactionPostingService(
        transactions=transactions,
        accounts=accounts,
        categories=categories,
    )


def get_create_expense_command(
    posting: Annotated[TransactionPostingService, Depends(get_posting_service)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> CreateExpenseCommand:
    return CreateExpenseCommand(posting, accounts)


def get_financial_expense_service(
    create_expense: Annotated[CreateExpenseCommand, Depends(get_create_expense_command)],
) -> FinancialExpenseService:
    return CreateExpenseFinancialExpenseService(create_expense)


def get_period_generator(
    periods: Annotated[TaxPeriodRepository, Depends(get_tax_period_repository)],
) -> TaxPeriodGenerator:
    return TaxPeriodGenerator(periods)


def get_tax_calculation_service() -> TaxCalculationService:
    return TaxCalculationService()


def get_create_tax_profile_command(
    profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> CreateTaxProfileCommand:
    return CreateTaxProfileCommand(profiles, accounts)


def get_update_tax_profile_command(
    profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> UpdateTaxProfileCommand:
    return UpdateTaxProfileCommand(profiles, accounts)


def get_create_tax_rule_command(
    profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
    rules: Annotated[TaxRuleRepository, Depends(get_tax_rule_repository)],
) -> CreateTaxRuleCommand:
    return CreateTaxRuleCommand(profiles, rules)


def get_update_tax_rule_command(
    profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
    rules: Annotated[TaxRuleRepository, Depends(get_tax_rule_repository)],
) -> UpdateTaxRuleCommand:
    return UpdateTaxRuleCommand(profiles, rules)


def get_archive_tax_rule_command(
    rules: Annotated[TaxRuleRepository, Depends(get_tax_rule_repository)],
) -> ArchiveTaxRuleCommand:
    return ArchiveTaxRuleCommand(rules)


def get_map_tax_category_command(
    profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
    categories: Annotated[CategoryRepository, Depends(get_category_repository)],
    mappings: Annotated[TaxCategoryMappingRepository, Depends(get_tax_category_mapping_repository)],
) -> MapTaxCategoryCommand:
    return MapTaxCategoryCommand(profiles, categories, mappings)


def get_override_transaction_command(
    profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
    transactions: Annotated[TransactionRepository, Depends(get_transaction_repository)],
    overrides: Annotated[
        TaxTransactionOverrideRepository,
        Depends(get_tax_transaction_override_repository),
    ],
) -> OverrideTransactionTaxTreatmentCommand:
    return OverrideTransactionTaxTreatmentCommand(profiles, transactions, overrides)


def get_calculate_tax_period_command(
    profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
    periods: Annotated[TaxPeriodRepository, Depends(get_tax_period_repository)],
    rules: Annotated[TaxRuleRepository, Depends(get_tax_rule_repository)],
    calculations: Annotated[TaxCalculationRepository, Depends(get_tax_calculation_repository)],
    mappings: Annotated[TaxCategoryMappingRepository, Depends(get_tax_category_mapping_repository)],
    overrides: Annotated[
        TaxTransactionOverrideRepository,
        Depends(get_tax_transaction_override_repository),
    ],
    read: Annotated[TaxReadRepository, Depends(get_tax_read_repository)],
    calculator: Annotated[TaxCalculationService, Depends(get_tax_calculation_service)],
    period_generator: Annotated[TaxPeriodGenerator, Depends(get_period_generator)],
) -> CalculateTaxPeriodCommand:
    return CalculateTaxPeriodCommand(
        profiles,
        periods,
        rules,
        calculations,
        mappings,
        overrides,
        read,
        calculator,
        period_generator,
    )


def get_record_tax_payment_command(
    periods: Annotated[TaxPeriodRepository, Depends(get_tax_period_repository)],
    payments: Annotated[TaxPaymentRepository, Depends(get_tax_payment_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    categories: Annotated[CategoryRepository, Depends(get_category_repository)],
    expenses: Annotated[FinancialExpenseService, Depends(get_financial_expense_service)],
) -> RecordTaxPaymentCommand:
    return RecordTaxPaymentCommand(periods, payments, accounts, categories, expenses)


def get_close_tax_period_command(
    periods: Annotated[TaxPeriodRepository, Depends(get_tax_period_repository)],
) -> CloseTaxPeriodCommand:
    return CloseTaxPeriodCommand(periods)


def get_get_tax_profile_query(
    profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
) -> GetTaxProfileQuery:
    return GetTaxProfileQuery(profiles)


def get_list_tax_profiles_query(
    profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
) -> ListTaxProfilesQuery:
    return ListTaxProfilesQuery(profiles)


def get_list_tax_rules_query(
    profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
    rules: Annotated[TaxRuleRepository, Depends(get_tax_rule_repository)],
) -> ListTaxRulesQuery:
    return ListTaxRulesQuery(profiles, rules)


def get_list_tax_periods_query(
    profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
    periods: Annotated[TaxPeriodRepository, Depends(get_tax_period_repository)],
    period_generator: Annotated[TaxPeriodGenerator, Depends(get_period_generator)],
) -> ListTaxPeriodsQuery:
    return ListTaxPeriodsQuery(profiles, periods, period_generator)


def get_get_tax_period_query(
    periods: Annotated[TaxPeriodRepository, Depends(get_tax_period_repository)],
    calculations: Annotated[TaxCalculationRepository, Depends(get_tax_calculation_repository)],
    payments: Annotated[TaxPaymentRepository, Depends(get_tax_payment_repository)],
) -> GetTaxPeriodQuery:
    return GetTaxPeriodQuery(periods, calculations, payments)


def get_tax_summary_query(
    profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
    periods: Annotated[TaxPeriodRepository, Depends(get_tax_period_repository)],
    calculations: Annotated[TaxCalculationRepository, Depends(get_tax_calculation_repository)],
    payments: Annotated[TaxPaymentRepository, Depends(get_tax_payment_repository)],
    read: Annotated[TaxReadRepository, Depends(get_tax_read_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    period_generator: Annotated[TaxPeriodGenerator, Depends(get_period_generator)],
) -> GetTaxSummaryQuery:
    return GetTaxSummaryQuery(
        profiles,
        periods,
        calculations,
        payments,
        read,
        accounts,
        period_generator,
    )


def get_tax_reserve_recommendation_query(
    summary: Annotated[GetTaxSummaryQuery, Depends(get_tax_summary_query)],
) -> GetTaxReserveRecommendationQuery:
    return GetTaxReserveRecommendationQuery(summary)
