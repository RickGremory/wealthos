"""FastAPI dependencies for the debts module."""

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
from wealthos.modules.debts.application.commands.archive_debt import ArchiveDebtCommand
from wealthos.modules.debts.application.commands.create_debt import CreateDebtCommand
from wealthos.modules.debts.application.commands.record_debt_payment import (
    RecordDebtPaymentCommand,
)
from wealthos.modules.debts.application.commands.update_debt import UpdateDebtCommand
from wealthos.modules.debts.application.queries.get_debt import GetDebtQuery
from wealthos.modules.debts.application.queries.get_debt_summary import (
    GetDebtSummaryQuery,
)
from wealthos.modules.debts.application.queries.get_payoff_plan import GetPayoffPlanQuery
from wealthos.modules.debts.application.queries.list_debt_payments import (
    ListDebtPaymentsQuery,
)
from wealthos.modules.debts.application.queries.list_debts import ListDebtsQuery
from wealthos.modules.debts.application.services.debt_payoff_calculator import (
    DebtPayoffCalculator,
)
from wealthos.modules.debts.application.services.debt_strategy_simulator import (
    DebtStrategySimulator,
)
from wealthos.modules.debts.application.services.financial_transfer_service import (
    CreateTransferFinancialTransferService,
    FinancialTransferService,
)
from wealthos.modules.debts.domain.repositories.debt_payment_repository import (
    DebtPaymentRepository,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.debts.infrastructure.repositories import (
    SqlAlchemyDebtPaymentRepository,
    SqlAlchemyDebtRepository,
)
from wealthos.modules.transactions.application.commands.create_transfer import (
    CreateTransferCommand,
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


def get_debt_repository(
    session: Annotated[Session, Depends(get_db)],
) -> DebtRepository:
    return SqlAlchemyDebtRepository(session)


def get_debt_payment_repository(
    session: Annotated[Session, Depends(get_db)],
) -> DebtPaymentRepository:
    return SqlAlchemyDebtPaymentRepository(session)


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


def get_create_transfer_command(
    posting: Annotated[TransactionPostingService, Depends(get_posting_service)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> CreateTransferCommand:
    return CreateTransferCommand(posting, accounts)


def get_financial_transfer_service(
    create_transfer: Annotated[CreateTransferCommand, Depends(get_create_transfer_command)],
) -> FinancialTransferService:
    return CreateTransferFinancialTransferService(create_transfer)


def get_payoff_calculator() -> DebtPayoffCalculator:
    return DebtPayoffCalculator()


def get_strategy_simulator() -> DebtStrategySimulator:
    return DebtStrategySimulator()


def get_create_debt_command(
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> CreateDebtCommand:
    return CreateDebtCommand(debts, accounts)


def get_update_debt_command(
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
) -> UpdateDebtCommand:
    return UpdateDebtCommand(debts)


def get_archive_debt_command(
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
) -> ArchiveDebtCommand:
    return ArchiveDebtCommand(debts)


def get_record_debt_payment_command(
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
    payments: Annotated[DebtPaymentRepository, Depends(get_debt_payment_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    transfers: Annotated[FinancialTransferService, Depends(get_financial_transfer_service)],
) -> RecordDebtPaymentCommand:
    return RecordDebtPaymentCommand(debts, payments, accounts, transfers)


def get_get_debt_query(
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    calculator: Annotated[DebtPayoffCalculator, Depends(get_payoff_calculator)],
) -> GetDebtQuery:
    return GetDebtQuery(debts, accounts, calculator)


def get_list_debts_query(
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    calculator: Annotated[DebtPayoffCalculator, Depends(get_payoff_calculator)],
) -> ListDebtsQuery:
    return ListDebtsQuery(debts, accounts, calculator)


def get_list_debt_payments_query(
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
    payments: Annotated[DebtPaymentRepository, Depends(get_debt_payment_repository)],
) -> ListDebtPaymentsQuery:
    return ListDebtPaymentsQuery(debts, payments)


def get_debt_summary_query(
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> GetDebtSummaryQuery:
    return GetDebtSummaryQuery(debts, accounts)


def get_payoff_plan_query(
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    simulator: Annotated[DebtStrategySimulator, Depends(get_strategy_simulator)],
) -> GetPayoffPlanQuery:
    return GetPayoffPlanQuery(debts, accounts, simulator)
