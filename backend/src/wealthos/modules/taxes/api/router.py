"""HTTP routes for taxes nested under organizations."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from wealthos.core.security.current_user import CurrentUser
from wealthos.core.security.organization_access import OrganizationMember
from wealthos.core.security.organization_permissions import require_organization_role
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.taxes.api.dependencies import (
    get_archive_tax_rule_command,
    get_calculate_tax_period_command,
    get_close_tax_period_command,
    get_create_tax_profile_command,
    get_create_tax_rule_command,
    get_get_tax_period_query,
    get_get_tax_profile_query,
    get_list_tax_periods_query,
    get_list_tax_profiles_query,
    get_list_tax_rules_query,
    get_map_tax_category_command,
    get_override_transaction_command,
    get_record_tax_payment_command,
    get_tax_reserve_recommendation_query,
    get_tax_summary_query,
    get_unit_of_work,
    get_update_tax_profile_command,
    get_update_tax_rule_command,
)
from wealthos.modules.taxes.application.commands.archive_tax_rule import (
    ArchiveTaxRuleCommand,
    ArchiveTaxRuleInput,
)
from wealthos.modules.taxes.application.commands.calculate_tax_period import (
    CalculateTaxPeriodCommand,
)
from wealthos.modules.taxes.application.commands.close_tax_period import (
    CloseTaxPeriodCommand,
    CloseTaxPeriodInput,
)
from wealthos.modules.taxes.application.commands.create_tax_profile import (
    CreateTaxProfileCommand,
    CreateTaxProfileInput,
)
from wealthos.modules.taxes.application.commands.create_tax_rule import (
    CreateTaxRuleCommand,
    CreateTaxRuleInput,
)
from wealthos.modules.taxes.application.commands.map_tax_category import (
    MapTaxCategoryCommand,
    MapTaxCategoryInput,
)
from wealthos.modules.taxes.application.commands.override_transaction_tax_treatment import (
    OverrideTransactionTaxTreatmentCommand,
    OverrideTransactionTaxTreatmentInput,
)
from wealthos.modules.taxes.application.commands.record_tax_payment import (
    RecordTaxPaymentCommand,
    RecordTaxPaymentInput,
)
from wealthos.modules.taxes.application.commands.update_tax_profile import (
    UpdateTaxProfileCommand,
    UpdateTaxProfileInput,
)
from wealthos.modules.taxes.application.commands.update_tax_rule import (
    UpdateTaxRuleCommand,
    UpdateTaxRuleInput,
)
from wealthos.modules.taxes.application.queries.get_tax_period import GetTaxPeriodQuery
from wealthos.modules.taxes.application.queries.get_tax_profile import GetTaxProfileQuery
from wealthos.modules.taxes.application.queries.get_tax_reserve_recommendation import (
    GetTaxReserveRecommendationQuery,
)
from wealthos.modules.taxes.application.queries.get_tax_summary import GetTaxSummaryQuery
from wealthos.modules.taxes.application.queries.list_tax_periods import ListTaxPeriodsQuery
from wealthos.modules.taxes.application.queries.list_tax_profiles import ListTaxProfilesQuery
from wealthos.modules.taxes.application.queries.list_tax_rules import ListTaxRulesQuery
from wealthos.modules.taxes.domain.exceptions import (
    InvalidCountryCode,
    InvalidFilingFrequency,
    InvalidFiscalYearStartMonth,
    InvalidPercentage,
    InvalidTaxBaseType,
    InvalidTaxInclusionMode,
    InvalidTaxpayerType,
    InvalidTaxPeriod,
    InvalidTaxRule,
    InvalidTaxTreatment,
    InvalidTaxType,
    TaxCategoryNotFound,
    TaxError,
    TaxPaymentAmountInvalid,
    TaxPaymentSourceInvalid,
    TaxPeriodAlreadyClosed,
    TaxPeriodClosed,
    TaxPeriodNotCalculated,
    TaxPeriodNotFound,
    TaxProfileAlreadyActive,
    TaxProfileNotFound,
    TaxReserveAccountInvalid,
    TaxRuleAlreadyArchived,
    TaxRuleNameEmpty,
    TaxRuleNameTooLong,
    TaxRuleNotFound,
    TaxTransactionNotFound,
)
from wealthos.modules.taxes.schemas.create import TaxProfileCreate
from wealthos.modules.taxes.schemas.response import (
    TaxCalculationResponse,
    TaxCategoryMappingResponse,
    TaxPaymentResponse,
    TaxPeriodListResponse,
    TaxPeriodResponse,
    TaxProfileListResponse,
    TaxProfileResponse,
    TaxRuleListResponse,
    TaxRuleResponse,
    TaxTransactionOverrideResponse,
)
from wealthos.modules.taxes.schemas.summary import (
    TaxReserveRecommendationListResponse,
    TaxSummaryResponse,
)
from wealthos.modules.taxes.schemas.update import (
    TaxCategoryMappingCreate,
    TaxPaymentCreate,
    TaxProfileUpdate,
    TaxRuleCreate,
    TaxRuleUpdate,
    TaxTransactionOverrideCreate,
)
from wealthos.shared.domain.exceptions import InvalidCurrency
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

router = APIRouter()

TAXES_DESCRIPTION = (
    "Tax endpoints provide **operational estimates** based on configured rules and "
    "posted transactions. They do not constitute formal tax advice or filing-ready returns."
)

RequireWriter = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin", "member")),
]
RequireManager = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin")),
]


def _http_map_tax_errors(exc: Exception) -> HTTPException:
    if isinstance(
        exc,
        TaxProfileNotFound
        | TaxRuleNotFound
        | TaxPeriodNotFound
        | TaxCategoryNotFound
        | TaxTransactionNotFound,
    ):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(
        exc,
        TaxRuleNameEmpty
        | TaxRuleNameTooLong
        | InvalidCountryCode
        | InvalidTaxpayerType
        | InvalidFilingFrequency
        | InvalidFiscalYearStartMonth
        | InvalidTaxType
        | InvalidTaxBaseType
        | InvalidTaxTreatment
        | InvalidTaxInclusionMode
        | InvalidTaxRule
        | InvalidTaxPeriod
        | InvalidPercentage
        | TaxPaymentAmountInvalid
        | InvalidCurrency,
    ):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    if isinstance(exc, TaxProfileAlreadyActive | TaxRuleAlreadyArchived | TaxPeriodAlreadyClosed):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(
        exc,
        TaxReserveAccountInvalid
        | TaxPaymentSourceInvalid
        | TaxPeriodClosed
        | TaxPeriodNotCalculated,
    ):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, TaxError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
    "/{organization_id}/tax-profiles",
    response_model=TaxProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create tax profile",
    description=TAXES_DESCRIPTION,
)
def create_tax_profile(
    organization_id: UUID,
    payload: TaxProfileCreate,
    _membership: RequireManager,
    command: Annotated[CreateTaxProfileCommand, Depends(get_create_tax_profile_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TaxProfileResponse:
    try:
        with uow:
            profile = command.execute(
                CreateTaxProfileInput(
                    organization_id=organization_id,
                    country_code=payload.country_code.upper(),
                    taxpayer_type=payload.taxpayer_type,
                    filing_frequency=payload.filing_frequency,
                    currency=payload.currency.upper(),
                    fiscal_year_start_month=payload.fiscal_year_start_month,
                    jurisdiction=payload.jurisdiction,
                    tax_regime=payload.tax_regime,
                    reserve_account_id=payload.reserve_account_id,
                )
            )
            uow.commit()
    except TaxError as exc:
        raise _http_map_tax_errors(exc) from exc
    return TaxProfileResponse.from_entity(profile)


@router.get(
    "/{organization_id}/tax-profiles",
    response_model=TaxProfileListResponse,
    summary="List tax profiles",
    description=TAXES_DESCRIPTION,
)
def list_tax_profiles(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListTaxProfilesQuery, Depends(get_list_tax_profiles_query)],
) -> TaxProfileListResponse:
    items = query.execute(organization_id)
    return TaxProfileListResponse(
        items=[TaxProfileResponse.from_entity(item) for item in items],
        total=len(items),
    )


@router.get(
    "/{organization_id}/tax-profiles/{profile_id}",
    response_model=TaxProfileResponse,
    summary="Get tax profile",
    description=TAXES_DESCRIPTION,
)
def get_tax_profile(
    organization_id: UUID,
    profile_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetTaxProfileQuery, Depends(get_get_tax_profile_query)],
) -> TaxProfileResponse:
    try:
        profile = query.execute(organization_id, profile_id)
    except TaxProfileNotFound as exc:
        raise _http_map_tax_errors(exc) from exc
    return TaxProfileResponse.from_entity(profile)


@router.patch(
    "/{organization_id}/tax-profiles/{profile_id}",
    response_model=TaxProfileResponse,
    summary="Update tax profile",
    description=TAXES_DESCRIPTION,
)
def update_tax_profile(
    organization_id: UUID,
    profile_id: UUID,
    payload: TaxProfileUpdate,
    _membership: RequireManager,
    command: Annotated[UpdateTaxProfileCommand, Depends(get_update_tax_profile_command)],
    query: Annotated[GetTaxProfileQuery, Depends(get_get_tax_profile_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TaxProfileResponse:
    try:
        with uow:
            command.execute(
                UpdateTaxProfileInput(
                    organization_id=organization_id,
                    profile_id=profile_id,
                    jurisdiction=payload.jurisdiction,
                    tax_regime=payload.tax_regime,
                    filing_frequency=payload.filing_frequency,
                    fiscal_year_start_month=payload.fiscal_year_start_month,
                    reserve_account_id=payload.reserve_account_id,
                    clear_reserve_account=payload.clear_reserve_account,
                    fields_set=frozenset(payload.model_fields_set),
                )
            )
            uow.commit()
    except TaxError as exc:
        raise _http_map_tax_errors(exc) from exc
    profile = query.execute(organization_id, profile_id)
    return TaxProfileResponse.from_entity(profile)


@router.post(
    "/{organization_id}/tax-profiles/{profile_id}/category-mappings",
    response_model=TaxCategoryMappingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Map category tax treatment",
    description=TAXES_DESCRIPTION,
)
def map_tax_category(
    organization_id: UUID,
    profile_id: UUID,
    payload: TaxCategoryMappingCreate,
    _membership: RequireWriter,
    command: Annotated[MapTaxCategoryCommand, Depends(get_map_tax_category_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TaxCategoryMappingResponse:
    try:
        with uow:
            mapping = command.execute(
                MapTaxCategoryInput(
                    organization_id=organization_id,
                    tax_profile_id=profile_id,
                    category_id=payload.category_id,
                    tax_treatment=payload.tax_treatment,
                    deductibility_percentage=payload.deductibility_percentage,
                )
            )
            uow.commit()
    except TaxError as exc:
        raise _http_map_tax_errors(exc) from exc
    return TaxCategoryMappingResponse.from_entity(mapping)


@router.post(
    "/{organization_id}/tax-profiles/{profile_id}/transaction-overrides",
    response_model=TaxTransactionOverrideResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Override transaction tax treatment",
    description=TAXES_DESCRIPTION,
)
def override_transaction_tax_treatment(
    organization_id: UUID,
    profile_id: UUID,
    payload: TaxTransactionOverrideCreate,
    current_user: CurrentUser,
    _membership: RequireWriter,
    command: Annotated[
        OverrideTransactionTaxTreatmentCommand,
        Depends(get_override_transaction_command),
    ],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TaxTransactionOverrideResponse:
    try:
        with uow:
            override = command.execute(
                OverrideTransactionTaxTreatmentInput(
                    organization_id=organization_id,
                    tax_profile_id=profile_id,
                    transaction_id=payload.transaction_id,
                    tax_treatment=payload.tax_treatment,
                    created_by_user_id=current_user.id,
                    deductibility_percentage=payload.deductibility_percentage,
                    reason=payload.reason,
                )
            )
            uow.commit()
    except TaxError as exc:
        raise _http_map_tax_errors(exc) from exc
    return TaxTransactionOverrideResponse.from_entity(override)


@router.post(
    "/{organization_id}/tax-rules",
    response_model=TaxRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create tax rule",
    description=TAXES_DESCRIPTION,
)
def create_tax_rule(
    organization_id: UUID,
    payload: TaxRuleCreate,
    _membership: RequireManager,
    command: Annotated[CreateTaxRuleCommand, Depends(get_create_tax_rule_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TaxRuleResponse:
    try:
        with uow:
            rule = command.execute(
                CreateTaxRuleInput(
                    organization_id=organization_id,
                    tax_profile_id=payload.tax_profile_id,
                    name=payload.name,
                    tax_type=payload.tax_type,
                    calculation_method=payload.calculation_method,
                    applies_to=payload.applies_to,
                    effective_from=payload.effective_from,
                    rate=payload.rate,
                    fixed_amount=payload.fixed_amount,
                    tax_inclusion_mode=payload.tax_inclusion_mode,
                    category_ids=tuple(payload.category_ids),
                    priority=payload.priority,
                    effective_to=payload.effective_to,
                )
            )
            uow.commit()
    except TaxError as exc:
        raise _http_map_tax_errors(exc) from exc
    return TaxRuleResponse.from_entity(rule)


@router.get(
    "/{organization_id}/tax-rules",
    response_model=TaxRuleListResponse,
    summary="List tax rules",
    description=TAXES_DESCRIPTION,
)
def list_tax_rules(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListTaxRulesQuery, Depends(get_list_tax_rules_query)],
    tax_profile_id: Annotated[UUID, Query()],
    include_archived: bool = Query(default=False),
) -> TaxRuleListResponse:
    try:
        items = query.execute(
            organization_id,
            tax_profile_id,
            include_archived=include_archived,
        )
    except TaxProfileNotFound as exc:
        raise _http_map_tax_errors(exc) from exc
    return TaxRuleListResponse(
        items=[TaxRuleResponse.from_entity(item) for item in items],
        total=len(items),
    )


@router.patch(
    "/{organization_id}/tax-rules/{rule_id}",
    response_model=TaxRuleResponse,
    summary="Update tax rule",
    description=TAXES_DESCRIPTION,
)
def update_tax_rule(
    organization_id: UUID,
    rule_id: UUID,
    payload: TaxRuleUpdate,
    _membership: RequireManager,
    command: Annotated[UpdateTaxRuleCommand, Depends(get_update_tax_rule_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TaxRuleResponse:
    try:
        with uow:
            rule = command.execute(
                UpdateTaxRuleInput(
                    organization_id=organization_id,
                    rule_id=rule_id,
                    name=payload.name,
                    rate=payload.rate,
                    fixed_amount=payload.fixed_amount,
                    priority=payload.priority,
                    effective_from=payload.effective_from,
                    effective_to=payload.effective_to,
                    clear_effective_to=payload.clear_effective_to,
                    category_ids=tuple(payload.category_ids) if payload.category_ids else None,
                    fields_set=frozenset(payload.model_fields_set),
                )
            )
            uow.commit()
    except TaxError as exc:
        raise _http_map_tax_errors(exc) from exc
    return TaxRuleResponse.from_entity(rule)


@router.post(
    "/{organization_id}/tax-rules/{rule_id}/archive",
    response_model=TaxRuleResponse,
    summary="Archive tax rule",
    description=TAXES_DESCRIPTION,
)
def archive_tax_rule(
    organization_id: UUID,
    rule_id: UUID,
    _membership: RequireManager,
    command: Annotated[ArchiveTaxRuleCommand, Depends(get_archive_tax_rule_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TaxRuleResponse:
    try:
        with uow:
            rule = command.execute(
                ArchiveTaxRuleInput(organization_id=organization_id, rule_id=rule_id)
            )
            uow.commit()
    except TaxError as exc:
        raise _http_map_tax_errors(exc) from exc
    return TaxRuleResponse.from_entity(rule)


@router.get(
    "/{organization_id}/tax-periods",
    response_model=TaxPeriodListResponse,
    summary="List tax periods",
    description=TAXES_DESCRIPTION,
)
def list_tax_periods(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListTaxPeriodsQuery, Depends(get_list_tax_periods_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
    tax_profile_id: Annotated[UUID, Query()],
) -> TaxPeriodListResponse:
    try:
        with uow:
            items = query.execute(organization_id, tax_profile_id)
            # Period generation is idempotent; commit so newly created windows persist.
            uow.commit()
    except TaxProfileNotFound as exc:
        raise _http_map_tax_errors(exc) from exc
    return TaxPeriodListResponse(
        items=[TaxPeriodResponse.from_entity(item) for item in items],
        total=len(items),
    )


@router.get(
    "/{organization_id}/tax-periods/{period_id}",
    response_model=TaxPeriodResponse,
    summary="Get tax period",
    description=TAXES_DESCRIPTION,
)
def get_tax_period(
    organization_id: UUID,
    period_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetTaxPeriodQuery, Depends(get_get_tax_period_query)],
) -> TaxPeriodResponse:
    try:
        detail = query.execute(organization_id, period_id)
    except TaxPeriodNotFound as exc:
        raise _http_map_tax_errors(exc) from exc
    return TaxPeriodResponse.from_detail(detail)


@router.post(
    "/{organization_id}/tax-periods/{period_id}/calculate",
    response_model=TaxCalculationResponse,
    summary="Calculate tax period",
    description=TAXES_DESCRIPTION,
)
def calculate_tax_period(
    organization_id: UUID,
    period_id: UUID,
    current_user: CurrentUser,
    _membership: RequireWriter,
    command: Annotated[CalculateTaxPeriodCommand, Depends(get_calculate_tax_period_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TaxCalculationResponse:
    try:
        with uow:
            result = command.execute(organization_id, period_id, current_user.id)
            uow.commit()
    except TaxError as exc:
        raise _http_map_tax_errors(exc) from exc
    return TaxCalculationResponse.from_calculate_result(result)


@router.post(
    "/{organization_id}/tax-periods/{period_id}/payments",
    response_model=TaxPaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record tax payment",
    description=TAXES_DESCRIPTION,
)
def record_tax_payment(
    organization_id: UUID,
    period_id: UUID,
    payload: TaxPaymentCreate,
    current_user: CurrentUser,
    _membership: RequireWriter,
    command: Annotated[RecordTaxPaymentCommand, Depends(get_record_tax_payment_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> TaxPaymentResponse:
    try:
        with uow:
            payment = command.execute(
                RecordTaxPaymentInput(
                    organization_id=organization_id,
                    tax_period_id=period_id,
                    source_account_id=payload.source_account_id,
                    amount=payload.amount,
                    tax_type=payload.tax_type,
                    paid_at=payload.paid_at,
                    created_by_user_id=current_user.id,
                    reference=payload.reference,
                    notes=payload.notes,
                    idempotency_key=idempotency_key,
                )
            )
            uow.commit()
    except TaxError as exc:
        raise _http_map_tax_errors(exc) from exc
    return TaxPaymentResponse.from_entity(payment)


@router.post(
    "/{organization_id}/tax-periods/{period_id}/close",
    response_model=TaxPeriodResponse,
    summary="Close tax period",
    description=TAXES_DESCRIPTION,
)
def close_tax_period(
    organization_id: UUID,
    period_id: UUID,
    _membership: RequireManager,
    command: Annotated[CloseTaxPeriodCommand, Depends(get_close_tax_period_command)],
    query: Annotated[GetTaxPeriodQuery, Depends(get_get_tax_period_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TaxPeriodResponse:
    try:
        with uow:
            command.execute(
                CloseTaxPeriodInput(organization_id=organization_id, period_id=period_id)
            )
            uow.commit()
    except TaxError as exc:
        raise _http_map_tax_errors(exc) from exc
    detail = query.execute(organization_id, period_id)
    return TaxPeriodResponse.from_detail(detail)


@router.get(
    "/{organization_id}/taxes/summary",
    response_model=TaxSummaryResponse,
    summary="Tax summary",
    description=TAXES_DESCRIPTION,
)
def get_tax_summary(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetTaxSummaryQuery, Depends(get_tax_summary_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TaxSummaryResponse:
    with uow:
        summary = query.execute(organization_id)
        uow.commit()
    return TaxSummaryResponse.from_summary(summary)


@router.get(
    "/{organization_id}/taxes/reserve-recommendation",
    response_model=TaxReserveRecommendationListResponse,
    summary="Tax reserve recommendation",
    description=TAXES_DESCRIPTION,
)
def get_tax_reserve_recommendation(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[
        GetTaxReserveRecommendationQuery,
        Depends(get_tax_reserve_recommendation_query),
    ],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TaxReserveRecommendationListResponse:
    with uow:
        items = query.execute(organization_id)
        uow.commit()
    return TaxReserveRecommendationListResponse.from_items(items)
