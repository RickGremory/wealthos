"""FastAPI dependencies for the transactions module."""

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
from wealthos.modules.transactions.application.commands.create_adjustment import (
    CreateAdjustmentCommand,
)
from wealthos.modules.transactions.application.commands.create_expense import (
    CreateExpenseCommand,
)
from wealthos.modules.transactions.application.commands.create_income import (
    CreateIncomeCommand,
)
from wealthos.modules.transactions.application.commands.create_transfer import (
    CreateTransferCommand,
)
from wealthos.modules.transactions.application.commands.update_transaction import (
    UpdateTransactionCommand,
)
from wealthos.modules.transactions.application.commands.void_transaction import (
    VoidTransactionCommand,
)
from wealthos.modules.transactions.application.queries.get_transaction import (
    GetTransactionQuery,
)
from wealthos.modules.transactions.application.queries.list_transactions import (
    ListTransactionsQuery,
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


def get_transaction_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TransactionRepository:
    return SqlAlchemyTransactionRepository(session)


def get_account_repository(
    session: Annotated[Session, Depends(get_db)],
) -> AccountRepository:
    return SqlAlchemyAccountRepository(session)


def get_category_repository(
    session: Annotated[Session, Depends(get_db)],
) -> CategoryRepository:
    return SqlAlchemyCategoryRepository(session)


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


def get_create_income_command(
    posting: Annotated[TransactionPostingService, Depends(get_posting_service)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> CreateIncomeCommand:
    return CreateIncomeCommand(posting, accounts)


def get_create_expense_command(
    posting: Annotated[TransactionPostingService, Depends(get_posting_service)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> CreateExpenseCommand:
    return CreateExpenseCommand(posting, accounts)


def get_create_transfer_command(
    posting: Annotated[TransactionPostingService, Depends(get_posting_service)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> CreateTransferCommand:
    return CreateTransferCommand(posting, accounts)


def get_create_adjustment_command(
    posting: Annotated[TransactionPostingService, Depends(get_posting_service)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> CreateAdjustmentCommand:
    return CreateAdjustmentCommand(posting, accounts)


def get_update_transaction_command(
    transactions: Annotated[TransactionRepository, Depends(get_transaction_repository)],
    categories: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> UpdateTransactionCommand:
    return UpdateTransactionCommand(transactions, categories)


def get_void_transaction_command(
    transactions: Annotated[TransactionRepository, Depends(get_transaction_repository)],
    posting: Annotated[TransactionPostingService, Depends(get_posting_service)],
) -> VoidTransactionCommand:
    return VoidTransactionCommand(transactions, posting)


def get_get_transaction_query(
    transactions: Annotated[TransactionRepository, Depends(get_transaction_repository)],
) -> GetTransactionQuery:
    return GetTransactionQuery(transactions)


def get_list_transactions_query(
    transactions: Annotated[TransactionRepository, Depends(get_transaction_repository)],
) -> ListTransactionsQuery:
    return ListTransactionsQuery(transactions)
