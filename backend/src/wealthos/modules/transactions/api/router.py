"""HTTP routes for transactions nested under organizations."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from wealthos.core.security.current_user import CurrentUser
from wealthos.core.security.organization_access import OrganizationMember
from wealthos.core.security.organization_permissions import require_organization_role
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.transactions.api.dependencies import (
    get_create_adjustment_command,
    get_create_expense_command,
    get_create_income_command,
    get_create_transfer_command,
    get_get_transaction_query,
    get_list_transactions_query,
    get_unit_of_work,
    get_update_transaction_command,
    get_void_transaction_command,
)
from wealthos.modules.transactions.application.commands.create_adjustment import (
    CreateAdjustmentCommand,
    CreateAdjustmentInput,
)
from wealthos.modules.transactions.application.commands.create_expense import (
    CreateExpenseCommand,
    CreateExpenseInput,
)
from wealthos.modules.transactions.application.commands.create_income import (
    CreateIncomeCommand,
    CreateIncomeInput,
)
from wealthos.modules.transactions.application.commands.create_transfer import (
    CreateTransferCommand,
    CreateTransferInput,
)
from wealthos.modules.transactions.application.commands.update_transaction import (
    UpdateTransactionCommand,
    UpdateTransactionInput,
)
from wealthos.modules.transactions.application.commands.void_transaction import (
    VoidTransactionCommand,
    VoidTransactionInput,
)
from wealthos.modules.transactions.application.queries.get_transaction import (
    GetTransactionQuery,
)
from wealthos.modules.transactions.application.queries.list_transactions import (
    ListTransactionsQuery,
)
from wealthos.modules.transactions.domain.exceptions import (
    AccountInactive,
    AccountNotFoundError,
    CategoryInactive,
    CategoryNotAllowedForTransfer,
    CategoryNotFoundError,
    CrossCurrencyTransferNotSupported,
    EntryCurrencyMismatch,
    InvalidTransactionEntries,
    SameAccountTransfer,
    TransactionAlreadyVoided,
    TransactionCategoryTypeMismatch,
    TransactionDescriptionEmpty,
    TransactionDescriptionTooLong,
    TransactionError,
    TransactionNotFoundError,
    ZeroEntryAmount,
)
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionFilters,
)
from wealthos.modules.transactions.schemas.collection import TransactionListResponse
from wealthos.modules.transactions.schemas.create import (
    AdjustmentTransactionCreate,
    ExpenseTransactionCreate,
    IncomeTransactionCreate,
    TransactionCreate,
    TransferTransactionCreate,
)
from wealthos.modules.transactions.schemas.response import TransactionResponse
from wealthos.modules.transactions.schemas.update import TransactionUpdate
from wealthos.shared.domain.exceptions import CurrencyMismatch, InvalidCurrency
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

router = APIRouter()

RequireWriter = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin", "member")),
]
RequireVoider = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin")),
]


@router.post(
    "/{organization_id}/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create transaction",
)
def create_transaction(
    organization_id: UUID,
    payload: TransactionCreate,
    current_user: CurrentUser,
    _membership: RequireWriter,
    create_income: Annotated[CreateIncomeCommand, Depends(get_create_income_command)],
    create_expense: Annotated[CreateExpenseCommand, Depends(get_create_expense_command)],
    create_transfer: Annotated[CreateTransferCommand, Depends(get_create_transfer_command)],
    create_adjustment: Annotated[CreateAdjustmentCommand, Depends(get_create_adjustment_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TransactionResponse:
    try:
        with uow:
            if isinstance(payload, IncomeTransactionCreate):
                transaction = create_income.execute(
                    CreateIncomeInput(
                        organization_id=organization_id,
                        account_id=payload.account_id,
                        category_id=payload.category_id,
                        amount=payload.amount,
                        description=payload.description,
                        occurred_at=payload.occurred_at,
                        created_by_user_id=current_user.id,
                        notes=payload.notes,
                    )
                )
            elif isinstance(payload, ExpenseTransactionCreate):
                transaction = create_expense.execute(
                    CreateExpenseInput(
                        organization_id=organization_id,
                        account_id=payload.account_id,
                        category_id=payload.category_id,
                        amount=payload.amount,
                        description=payload.description,
                        occurred_at=payload.occurred_at,
                        created_by_user_id=current_user.id,
                        notes=payload.notes,
                    )
                )
            elif isinstance(payload, TransferTransactionCreate):
                transaction = create_transfer.execute(
                    CreateTransferInput(
                        organization_id=organization_id,
                        source_account_id=payload.source_account_id,
                        destination_account_id=payload.destination_account_id,
                        amount=payload.amount,
                        description=payload.description,
                        occurred_at=payload.occurred_at,
                        created_by_user_id=current_user.id,
                        notes=payload.notes,
                    )
                )
            elif isinstance(payload, AdjustmentTransactionCreate):
                transaction = create_adjustment.execute(
                    CreateAdjustmentInput(
                        organization_id=organization_id,
                        account_id=payload.account_id,
                        amount=payload.amount,
                        description=payload.description,
                        occurred_at=payload.occurred_at,
                        created_by_user_id=current_user.id,
                        category_id=payload.category_id,
                        notes=payload.notes,
                    )
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Unsupported transaction type.",
                )
            uow.commit()
    except (AccountNotFoundError, CategoryNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (
        TransactionDescriptionEmpty,
        TransactionDescriptionTooLong,
        InvalidCurrency,
        ZeroEntryAmount,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except (
        AccountInactive,
        CategoryInactive,
        CategoryNotAllowedForTransfer,
        CrossCurrencyTransferNotSupported,
        EntryCurrencyMismatch,
        InvalidTransactionEntries,
        SameAccountTransfer,
        TransactionCategoryTypeMismatch,
        CurrencyMismatch,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except TransactionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return TransactionResponse.from_entity(transaction)


@router.get(
    "/{organization_id}/transactions",
    response_model=TransactionListResponse,
    summary="List transactions",
)
def list_transactions(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListTransactionsQuery, Depends(get_list_transactions_query)],
    account_id: UUID | None = None,
    category_id: UUID | None = None,
    transaction_type: Annotated[
        str | None,
        Query(alias="type", pattern="^(income|expense|transfer|adjustment)$"),
    ] = None,
    status_filter: Annotated[
        str | None,
        Query(alias="status", pattern="^(posted|voided)$"),
    ] = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    search: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TransactionListResponse:
    result = query.execute(
        organization_id,
        TransactionFilters(
            account_id=account_id,
            category_id=category_id,
            transaction_type=transaction_type,
            status=status_filter,
            date_from=date_from,
            date_to=date_to,
            min_amount=min_amount,
            max_amount=max_amount,
            search=search,
            limit=limit,
            offset=offset,
        ),
    )
    return TransactionListResponse(
        items=[TransactionResponse.from_entity(item) for item in result.items],
        total=result.total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{organization_id}/transactions/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction",
)
def get_transaction(
    organization_id: UUID,
    transaction_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetTransactionQuery, Depends(get_get_transaction_query)],
) -> TransactionResponse:
    try:
        transaction = query.execute(organization_id, transaction_id)
    except TransactionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TransactionResponse.from_entity(transaction)


@router.patch(
    "/{organization_id}/transactions/{transaction_id}",
    response_model=TransactionResponse,
    summary="Update transaction metadata",
)
def update_transaction(
    organization_id: UUID,
    transaction_id: UUID,
    payload: TransactionUpdate,
    current_user: CurrentUser,
    _membership: RequireWriter,
    command: Annotated[UpdateTransactionCommand, Depends(get_update_transaction_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TransactionResponse:
    try:
        with uow:
            transaction = command.execute(
                UpdateTransactionInput(
                    organization_id=organization_id,
                    transaction_id=transaction_id,
                    updated_by_user_id=current_user.id,
                    description=payload.description,
                    notes=payload.notes,
                    occurred_at=payload.occurred_at,
                    category_id=payload.category_id,
                    fields_set=frozenset(payload.model_fields_set),
                )
            )
            uow.commit()
    except TransactionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CategoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (TransactionDescriptionEmpty, TransactionDescriptionTooLong) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except (
        CategoryInactive,
        CategoryNotAllowedForTransfer,
        TransactionAlreadyVoided,
        TransactionCategoryTypeMismatch,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except TransactionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return TransactionResponse.from_entity(transaction)


@router.post(
    "/{organization_id}/transactions/{transaction_id}/void",
    response_model=TransactionResponse,
    summary="Void transaction",
)
def void_transaction(
    organization_id: UUID,
    transaction_id: UUID,
    current_user: CurrentUser,
    _membership: RequireVoider,
    command: Annotated[VoidTransactionCommand, Depends(get_void_transaction_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TransactionResponse:
    try:
        with uow:
            transaction = command.execute(
                VoidTransactionInput(
                    organization_id=organization_id,
                    transaction_id=transaction_id,
                    voided_by_user_id=current_user.id,
                )
            )
            uow.commit()
    except TransactionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TransactionAlreadyVoided as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except TransactionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return TransactionResponse.from_entity(transaction)
