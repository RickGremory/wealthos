"""HTTP routes for accounts nested under organizations."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from wealthos.core.security.organization_access import OrganizationMember
from wealthos.core.security.organization_permissions import require_organization_role
from wealthos.modules.accounts.api.dependencies import (
    get_archive_account_command,
    get_create_account_command,
    get_get_account_query,
    get_list_accounts_query,
    get_unit_of_work,
    get_update_account_command,
)
from wealthos.modules.accounts.application.commands.archive_account import (
    ArchiveAccountCommand,
    ArchiveAccountInput,
)
from wealthos.modules.accounts.application.commands.create_account import (
    CreateAccountCommand,
    CreateAccountInput,
)
from wealthos.modules.accounts.application.commands.update_account import (
    UpdateAccountCommand,
    UpdateAccountInput,
)
from wealthos.modules.accounts.application.queries.get_account import GetAccountQuery
from wealthos.modules.accounts.application.queries.list_accounts import ListAccountsQuery
from wealthos.modules.accounts.domain.exceptions import (
    AccountAlreadyArchived,
    AccountError,
    AccountNameEmpty,
    AccountNameTooLong,
    AccountNotFoundError,
    InvalidAccountType,
    InvalidLastFour,
)
from wealthos.modules.accounts.schemas.collection import AccountListResponse
from wealthos.modules.accounts.schemas.create import AccountCreate
from wealthos.modules.accounts.schemas.response import AccountResponse
from wealthos.modules.accounts.schemas.update import AccountUpdate
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.shared.domain.exceptions import InvalidCurrency
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

router = APIRouter()

RequireWriter = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin", "member")),
]
RequireArchiver = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin")),
]


@router.post(
    "/{organization_id}/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create account",
)
def create_account(
    organization_id: UUID,
    payload: AccountCreate,
    _membership: RequireWriter,
    command: Annotated[CreateAccountCommand, Depends(get_create_account_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> AccountResponse:
    try:
        with uow:
            account = command.execute(
                CreateAccountInput(
                    organization_id=organization_id,
                    name=payload.name,
                    account_type=payload.account_type,
                    currency=payload.currency,
                    opening_balance=payload.opening_balance,
                    institution_name=payload.institution_name,
                    last_four=payload.last_four,
                )
            )
            uow.commit()
    except (
        AccountNameEmpty,
        AccountNameTooLong,
        InvalidAccountType,
        InvalidCurrency,
        InvalidLastFour,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except AccountError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AccountResponse.from_entity(account)


@router.get(
    "/{organization_id}/accounts",
    response_model=AccountListResponse,
    summary="List accounts",
)
def list_accounts(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListAccountsQuery, Depends(get_list_accounts_query)],
    include_archived: bool = Query(default=False),
) -> AccountListResponse:
    accounts = query.execute(organization_id, include_archived=include_archived)
    items = [AccountResponse.from_entity(account) for account in accounts]
    return AccountListResponse(items=items, total=len(items))


@router.get(
    "/{organization_id}/accounts/{account_id}",
    response_model=AccountResponse,
    summary="Get account",
)
def get_account(
    organization_id: UUID,
    account_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetAccountQuery, Depends(get_get_account_query)],
) -> AccountResponse:
    try:
        account = query.execute(organization_id, account_id)
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AccountResponse.from_entity(account)


@router.patch(
    "/{organization_id}/accounts/{account_id}",
    response_model=AccountResponse,
    summary="Update account",
)
def update_account(
    organization_id: UUID,
    account_id: UUID,
    payload: AccountUpdate,
    _membership: RequireWriter,
    command: Annotated[UpdateAccountCommand, Depends(get_update_account_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> AccountResponse:
    try:
        with uow:
            account = command.execute(
                UpdateAccountInput(
                    organization_id=organization_id,
                    account_id=account_id,
                    name=payload.name,
                    institution_name=payload.institution_name,
                    last_four=payload.last_four,
                    fields_set=frozenset(payload.model_fields_set),
                )
            )
            uow.commit()
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (AccountNameEmpty, AccountNameTooLong, InvalidLastFour) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except AccountError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AccountResponse.from_entity(account)


@router.post(
    "/{organization_id}/accounts/{account_id}/archive",
    response_model=AccountResponse,
    summary="Archive account",
)
def archive_account(
    organization_id: UUID,
    account_id: UUID,
    _membership: RequireArchiver,
    command: Annotated[ArchiveAccountCommand, Depends(get_archive_account_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> AccountResponse:
    try:
        with uow:
            account = command.execute(
                ArchiveAccountInput(
                    organization_id=organization_id,
                    account_id=account_id,
                )
            )
            uow.commit()
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AccountAlreadyArchived as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except AccountError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AccountResponse.from_entity(account)
