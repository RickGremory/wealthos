"""HTTP routes for debts nested under organizations."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from wealthos.core.security.current_user import CurrentUser
from wealthos.core.security.organization_access import OrganizationMember
from wealthos.core.security.organization_permissions import require_organization_role
from wealthos.modules.debts.api.dependencies import (
    get_archive_debt_command,
    get_create_debt_command,
    get_debt_summary_query,
    get_get_debt_query,
    get_list_debt_payments_query,
    get_list_debts_query,
    get_payoff_plan_query,
    get_record_debt_payment_command,
    get_unit_of_work,
    get_update_debt_command,
)
from wealthos.modules.debts.application.commands.archive_debt import (
    ArchiveDebtCommand,
    ArchiveDebtInput,
)
from wealthos.modules.debts.application.commands.create_debt import (
    CreateDebtCommand,
    CreateDebtInput,
)
from wealthos.modules.debts.application.commands.record_debt_payment import (
    RecordDebtPaymentCommand,
    RecordDebtPaymentInput,
)
from wealthos.modules.debts.application.commands.update_debt import (
    UpdateDebtCommand,
    UpdateDebtInput,
)
from wealthos.modules.debts.application.queries.get_debt import GetDebtQuery
from wealthos.modules.debts.application.queries.get_debt_summary import (
    GetDebtSummaryQuery,
)
from wealthos.modules.debts.application.queries.get_payoff_plan import GetPayoffPlanQuery
from wealthos.modules.debts.application.queries.list_debt_payments import (
    ListDebtPaymentsQuery,
)
from wealthos.modules.debts.application.queries.list_debts import ListDebtsQuery
from wealthos.modules.debts.domain.exceptions import (
    CannotUpdateDebtField,
    DebtAccountInactive,
    DebtAccountMustBeLiability,
    DebtAccountNotFound,
    DebtAlreadyArchived,
    DebtAlreadyExistsForAccount,
    DebtAlreadyPaidOff,
    DebtCurrencyMismatch,
    DebtError,
    DebtNameEmpty,
    DebtNameTooLong,
    DebtNotFoundError,
    DebtPaymentAmountInvalid,
    DebtPaymentBreakdownInvalid,
    DebtPaymentExceedsBalance,
    DebtPaymentSourceInvalid,
    InvalidDebtType,
    InvalidInterestRate,
    InvalidMinimumPayment,
    InvalidPaymentDay,
    InvalidPayoffStrategy,
)
from wealthos.modules.debts.schemas.create import DebtCreate
from wealthos.modules.debts.schemas.payment import DebtPaymentCreate
from wealthos.modules.debts.schemas.payoff_plan import PayoffPlanListResponse
from wealthos.modules.debts.schemas.response import (
    DebtListResponse,
    DebtPaymentListResponse,
    DebtPaymentResponse,
    DebtResponse,
)
from wealthos.modules.debts.schemas.summary import DebtSummaryResponse
from wealthos.modules.debts.schemas.update import DebtUpdate
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
RequireManager = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin")),
]


def _http_map_debt_errors(exc: Exception) -> HTTPException:
    if isinstance(exc, (DebtNotFoundError, DebtAccountNotFound)):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(
        exc,
        DebtNameEmpty
        | DebtNameTooLong
        | InvalidDebtType
        | InvalidInterestRate
        | InvalidMinimumPayment
        | InvalidPaymentDay
        | InvalidPayoffStrategy
        | DebtPaymentAmountInvalid
        | DebtPaymentBreakdownInvalid
        | InvalidCurrency,
    ):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    if isinstance(exc, (DebtAlreadyArchived, DebtAlreadyExistsForAccount)):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(
        exc,
        DebtAccountMustBeLiability
        | DebtAccountInactive
        | DebtCurrencyMismatch
        | DebtAlreadyPaidOff
        | DebtPaymentExceedsBalance
        | DebtPaymentSourceInvalid
        | CannotUpdateDebtField,
    ):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, DebtError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
    "/{organization_id}/debts",
    response_model=DebtResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create debt",
)
def create_debt(
    organization_id: UUID,
    payload: DebtCreate,
    _membership: RequireWriter,
    command: Annotated[CreateDebtCommand, Depends(get_create_debt_command)],
    query: Annotated[GetDebtQuery, Depends(get_get_debt_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> DebtResponse:
    try:
        with uow:
            debt = command.execute(
                CreateDebtInput(
                    organization_id=organization_id,
                    account_id=payload.account_id,
                    name=payload.name,
                    debt_type=payload.debt_type,
                    annual_interest_rate=payload.annual_interest_rate,
                    minimum_payment=payload.minimum_payment,
                    original_principal=payload.original_principal,
                    opened_at=payload.opened_at,
                    maturity_date=payload.maturity_date,
                    payment_day=payload.payment_day,
                    statement_day=payload.statement_day,
                    notes=payload.notes,
                )
            )
            uow.commit()
    except (DebtError, InvalidCurrency) as exc:
        raise _http_map_debt_errors(exc) from exc

    item = query.execute(organization_id, debt.id)
    return DebtResponse.from_debt_with_balance(item)


@router.get(
    "/{organization_id}/debts",
    response_model=DebtListResponse,
    summary="List debts",
)
def list_debts(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListDebtsQuery, Depends(get_list_debts_query)],
    status_filter: Annotated[
        str | None,
        Query(alias="status", pattern="^(active|paid_off|archived)$"),
    ] = None,
    debt_type: str | None = None,
    currency: str | None = None,
    include_archived: bool = Query(default=False),
) -> DebtListResponse:
    items = query.execute(
        organization_id,
        status=status_filter,
        debt_type=debt_type,
        currency=currency.upper() if currency else None,
        include_archived=include_archived,
    )
    return DebtListResponse(
        items=[DebtResponse.from_debt_with_balance(item) for item in items],
        total=len(items),
    )


@router.get(
    "/{organization_id}/debts/summary",
    response_model=DebtSummaryResponse,
    summary="Debt summary by currency",
)
def get_debt_summary(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetDebtSummaryQuery, Depends(get_debt_summary_query)],
) -> DebtSummaryResponse:
    summary = query.execute(organization_id)
    return DebtSummaryResponse.from_summary(summary)


@router.get(
    "/{organization_id}/debts/payoff-plan",
    response_model=PayoffPlanListResponse,
    summary="Debt payoff plan simulation",
)
def get_payoff_plan(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetPayoffPlanQuery, Depends(get_payoff_plan_query)],
    strategy: Annotated[
        Literal["avalanche", "snowball", "minimum_only"],
        Query(),
    ] = "avalanche",
    extra_monthly_payment: Annotated[Decimal, Query(ge=0)] = Decimal("0"),
) -> PayoffPlanListResponse:
    try:
        results = query.execute(
            organization_id,
            strategy=strategy,
            extra_monthly_payment=extra_monthly_payment,
        )
    except DebtError as exc:
        raise _http_map_debt_errors(exc) from exc
    return PayoffPlanListResponse.from_results(results)


@router.get(
    "/{organization_id}/debts/{debt_id}",
    response_model=DebtResponse,
    summary="Get debt",
)
def get_debt(
    organization_id: UUID,
    debt_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetDebtQuery, Depends(get_get_debt_query)],
) -> DebtResponse:
    try:
        item = query.execute(organization_id, debt_id)
    except DebtNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DebtResponse.from_debt_with_balance(item)


@router.patch(
    "/{organization_id}/debts/{debt_id}",
    response_model=DebtResponse,
    summary="Update debt metadata",
)
def update_debt(
    organization_id: UUID,
    debt_id: UUID,
    payload: DebtUpdate,
    _membership: RequireManager,
    command: Annotated[UpdateDebtCommand, Depends(get_update_debt_command)],
    query: Annotated[GetDebtQuery, Depends(get_get_debt_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> DebtResponse:
    try:
        with uow:
            command.execute(
                UpdateDebtInput(
                    organization_id=organization_id,
                    debt_id=debt_id,
                    name=payload.name,
                    annual_interest_rate=payload.annual_interest_rate,
                    minimum_payment=payload.minimum_payment,
                    maturity_date=payload.maturity_date,
                    payment_day=payload.payment_day,
                    statement_day=payload.statement_day,
                    notes=payload.notes,
                    fields_set=frozenset(payload.model_fields_set),
                )
            )
            uow.commit()
    except DebtError as exc:
        raise _http_map_debt_errors(exc) from exc

    item = query.execute(organization_id, debt_id)
    return DebtResponse.from_debt_with_balance(item)


@router.post(
    "/{organization_id}/debts/{debt_id}/payments",
    response_model=DebtPaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record debt payment",
)
def record_debt_payment(
    organization_id: UUID,
    debt_id: UUID,
    payload: DebtPaymentCreate,
    current_user: CurrentUser,
    _membership: RequireWriter,
    command: Annotated[RecordDebtPaymentCommand, Depends(get_record_debt_payment_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> DebtPaymentResponse:
    try:
        with uow:
            result = command.execute(
                RecordDebtPaymentInput(
                    organization_id=organization_id,
                    debt_id=debt_id,
                    source_account_id=payload.source_account_id,
                    amount=payload.amount,
                    occurred_at=payload.occurred_at,
                    created_by_user_id=current_user.id,
                    description=payload.description,
                    principal_amount=payload.principal_amount,
                    interest_amount=payload.interest_amount,
                )
            )
            uow.commit()
    except DebtError as exc:
        raise _http_map_debt_errors(exc) from exc

    return DebtPaymentResponse.from_entity(result.payment)


@router.get(
    "/{organization_id}/debts/{debt_id}/payments",
    response_model=DebtPaymentListResponse,
    summary="List debt payments",
)
def list_debt_payments(
    organization_id: UUID,
    debt_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListDebtPaymentsQuery, Depends(get_list_debt_payments_query)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> DebtPaymentListResponse:
    try:
        result = query.execute(organization_id, debt_id, limit=limit, offset=offset)
    except DebtNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DebtPaymentListResponse(
        items=[DebtPaymentResponse.from_entity(item) for item in result.items],
        total=result.total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/{organization_id}/debts/{debt_id}/archive",
    response_model=DebtResponse,
    summary="Archive debt",
)
def archive_debt(
    organization_id: UUID,
    debt_id: UUID,
    _membership: RequireManager,
    command: Annotated[ArchiveDebtCommand, Depends(get_archive_debt_command)],
    query: Annotated[GetDebtQuery, Depends(get_get_debt_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> DebtResponse:
    try:
        with uow:
            command.execute(ArchiveDebtInput(organization_id=organization_id, debt_id=debt_id))
            uow.commit()
    except DebtError as exc:
        raise _http_map_debt_errors(exc) from exc

    item = query.execute(organization_id, debt_id)
    return DebtResponse.from_debt_with_balance(item)
