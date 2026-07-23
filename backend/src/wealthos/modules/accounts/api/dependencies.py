"""FastAPI dependencies for the accounts module."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.modules.accounts.application.commands.archive_account import (
    ArchiveAccountCommand,
)
from wealthos.modules.accounts.application.commands.create_account import (
    CreateAccountCommand,
)
from wealthos.modules.accounts.application.commands.update_account import (
    UpdateAccountCommand,
)
from wealthos.modules.accounts.application.queries.get_account import GetAccountQuery
from wealthos.modules.accounts.application.queries.list_accounts import ListAccountsQuery
from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.accounts.infrastructure.repositories import (
    SqlAlchemyAccountRepository,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


def get_unit_of_work(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_account_repository(
    session: Annotated[Session, Depends(get_db)],
) -> AccountRepository:
    return SqlAlchemyAccountRepository(session)


def get_create_account_command(
    repository: Annotated[AccountRepository, Depends(get_account_repository)],
) -> CreateAccountCommand:
    return CreateAccountCommand(repository)


def get_update_account_command(
    repository: Annotated[AccountRepository, Depends(get_account_repository)],
) -> UpdateAccountCommand:
    return UpdateAccountCommand(repository)


def get_archive_account_command(
    repository: Annotated[AccountRepository, Depends(get_account_repository)],
) -> ArchiveAccountCommand:
    return ArchiveAccountCommand(repository)


def get_get_account_query(
    repository: Annotated[AccountRepository, Depends(get_account_repository)],
) -> GetAccountQuery:
    return GetAccountQuery(repository)


def get_list_accounts_query(
    repository: Annotated[AccountRepository, Depends(get_account_repository)],
) -> ListAccountsQuery:
    return ListAccountsQuery(repository)
