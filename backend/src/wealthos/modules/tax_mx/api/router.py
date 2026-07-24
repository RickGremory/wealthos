"""HTTP routes for Mexico tax specialization nested under organizations."""

from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from wealthos.core.security.current_user import CurrentUser
from wealthos.core.security.organization_access import OrganizationMember
from wealthos.core.security.organization_permissions import require_organization_role
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.tax_mx.api.dependencies import (
    get_calculate_command,
    get_catalogs_query,
    get_classify_command,
    get_configuration_query,
    get_create_configuration_command,
    get_list_mappings_query,
    get_map_category_command,
    get_revise_configuration_command,
    get_summary_query,
    get_unclassified_query,
    get_unit_of_work,
    get_update_mapping_command,
    get_workpaper_query,
)
from wealthos.modules.tax_mx.application.commands.calculate_mexico_tax_period import (
    CalculateMexicoTaxPeriodCommand,
)
from wealthos.modules.tax_mx.application.commands.classify_mexico_tax_transaction import (
    ClassifyMexicoTaxTransactionCommand,
    ClassifyMexicoTaxTransactionInput,
)
from wealthos.modules.tax_mx.application.commands.create_mexico_tax_configuration import (
    CreateMexicoTaxConfigurationCommand,
    CreateMexicoTaxConfigurationInput,
)
from wealthos.modules.tax_mx.application.commands.map_mexico_tax_category import (
    MapMexicoTaxCategoryCommand,
    MapMexicoTaxCategoryInput,
    UpdateMexicoTaxCategoryMappingCommand,
    UpdateMexicoTaxCategoryMappingInput,
)
from wealthos.modules.tax_mx.application.commands.revise_mexico_tax_configuration import (
    ReviseMexicoTaxConfigurationCommand,
    ReviseMexicoTaxConfigurationInput,
)
from wealthos.modules.tax_mx.application.queries.mexico_tax_queries import (
    GetMexicoTaxConfigurationQuery,
    GetMexicoTaxSummaryQuery,
    GetMexicoTaxWorkpaperQuery,
    ListMexicoCategoryMappingsQuery,
    ListMexicoTaxCatalogsQuery,
    ListUnclassifiedTaxTransactionsQuery,
)
from wealthos.modules.tax_mx.domain.exceptions import TaxMxError
from wealthos.modules.tax_mx.schemas.configuration import (
    CatalogListResponse,
    MexicoCategoryMappingCreate,
    MexicoCategoryMappingResponse,
    MexicoCategoryMappingUpdate,
    MexicoClassificationCreate,
    MexicoTaxConfigurationCreate,
    MexicoTaxConfigurationResponse,
    MexicoTaxConfigurationUpdate,
    MexicoTaxSummaryResponse,
    MexicoWorkpaperResponse,
    UnclassifiedTransactionItem,
    UnclassifiedTransactionListResponse,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

router = APIRouter()

MX_DESCRIPTION = (
    "Mexican tax specialization estimates. Results are operational preparations, "
    "not official SAT filings or professional tax advice."
)

RequireManager = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin")),
]
RequireWriter = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin", "member")),
]


def _http_map(exc: Exception) -> HTTPException:
    message = str(exc)
    name = type(exc).__name__
    if "NotFound" in name or "Required" in name:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    if "Overlap" in name or "Incompatible" in name or "Closed" in name:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)
    if "Invalid" in name or "CashFlow" in name or "Regime" in name:
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


@router.post(
    "/{organization_id}/taxes/mx/configuration",
    response_model=MexicoTaxConfigurationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Mexico tax configuration",
    description=MX_DESCRIPTION,
)
def create_configuration(
    organization_id: UUID,
    payload: MexicoTaxConfigurationCreate,
    _membership: RequireManager,
    command: Annotated[
        CreateMexicoTaxConfigurationCommand, Depends(get_create_configuration_command)
    ],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> MexicoTaxConfigurationResponse:
    estimation = payload.income_tax_estimation
    try:
        with uow:
            entity = command.execute(
                CreateMexicoTaxConfigurationInput(
                    organization_id=organization_id,
                    tax_profile_id=payload.tax_profile_id,
                    rfc=payload.rfc,
                    person_type=payload.person_type,
                    tax_regime_code=payload.tax_regime_code,
                    vat_enabled=payload.vat_enabled,
                    income_tax_enabled=payload.income_tax_enabled,
                    effective_from=payload.effective_from,
                    default_vat_rate=payload.default_vat_rate,
                    income_tax_estimation_method=estimation.method if estimation else None,
                    income_tax_estimation_base=estimation.base if estimation else None,
                    income_tax_estimation_rate=estimation.rate if estimation else None,
                    requires_invoice_evidence=payload.requires_invoice_evidence,
                )
            )
            uow.commit()
    except TaxMxError as exc:
        raise _http_map(exc) from exc
    return MexicoTaxConfigurationResponse.from_entity(entity)


@router.get(
    "/{organization_id}/taxes/mx/configuration",
    response_model=MexicoTaxConfigurationResponse,
    summary="Get current Mexico tax configuration",
    description=MX_DESCRIPTION,
)
def get_configuration(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetMexicoTaxConfigurationQuery, Depends(get_configuration_query)],
    tax_profile_id: Annotated[UUID | None, Query()] = None,
) -> MexicoTaxConfigurationResponse:
    try:
        entity = query.execute(organization_id, tax_profile_id)
    except TaxMxError as exc:
        raise _http_map(exc) from exc
    return MexicoTaxConfigurationResponse.from_entity(entity)


@router.patch(
    "/{organization_id}/taxes/mx/configuration",
    response_model=MexicoTaxConfigurationResponse,
    summary="Revise Mexico tax configuration (versioned)",
    description=MX_DESCRIPTION,
)
def revise_configuration(
    organization_id: UUID,
    payload: MexicoTaxConfigurationUpdate,
    _membership: RequireManager,
    get_query: Annotated[GetMexicoTaxConfigurationQuery, Depends(get_configuration_query)],
    command: Annotated[
        ReviseMexicoTaxConfigurationCommand, Depends(get_revise_configuration_command)
    ],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> MexicoTaxConfigurationResponse:
    try:
        current = get_query.execute(organization_id)
        estimation = payload.income_tax_estimation
        with uow:
            entity = command.execute(
                ReviseMexicoTaxConfigurationInput(
                    organization_id=organization_id,
                    tax_profile_id=current.tax_profile_id,
                    rfc=payload.rfc,
                    person_type=payload.person_type,
                    tax_regime_code=payload.tax_regime_code,
                    vat_enabled=payload.vat_enabled,
                    income_tax_enabled=payload.income_tax_enabled,
                    effective_from=payload.effective_from,
                    default_vat_rate=payload.default_vat_rate,
                    income_tax_estimation_method=estimation.method if estimation else None,
                    income_tax_estimation_base=estimation.base if estimation else None,
                    income_tax_estimation_rate=estimation.rate if estimation else None,
                    requires_invoice_evidence=payload.requires_invoice_evidence,
                )
            )
            uow.commit()
    except TaxMxError as exc:
        raise _http_map(exc) from exc
    return MexicoTaxConfigurationResponse.from_entity(entity)


@router.get(
    "/{organization_id}/taxes/mx/catalogs",
    response_model=CatalogListResponse,
    summary="List Mexico tax catalogs",
    description=MX_DESCRIPTION,
)
def list_catalogs(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListMexicoTaxCatalogsQuery, Depends(get_catalogs_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CatalogListResponse:
    with uow:
        payload = query.execute()
        uow.commit()
    return CatalogListResponse(**payload)


@router.post(
    "/{organization_id}/taxes/mx/category-mappings",
    response_model=MexicoCategoryMappingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Map category to Mexico tax treatments",
)
def create_mapping(
    organization_id: UUID,
    payload: MexicoCategoryMappingCreate,
    _membership: RequireManager,
    command: Annotated[MapMexicoTaxCategoryCommand, Depends(get_map_category_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> MexicoCategoryMappingResponse:
    try:
        with uow:
            mapping = command.execute(
                MapMexicoTaxCategoryInput(
                    organization_id=organization_id,
                    tax_profile_id=payload.tax_profile_id,
                    category_id=payload.category_id,
                    vat_treatment=payload.vat_treatment,
                    income_treatment=payload.income_treatment,
                    expense_treatment=payload.expense_treatment,
                    deductibility_percentage=payload.deductibility_percentage,
                    vat_creditable_percentage=payload.vat_creditable_percentage,
                    requires_cfdi=payload.requires_cfdi,
                    requires_payment_evidence=payload.requires_payment_evidence,
                )
            )
            uow.commit()
    except TaxMxError as exc:
        raise _http_map(exc) from exc
    return MexicoCategoryMappingResponse(
        id=mapping.id,
        tax_profile_id=mapping.tax_profile_id,
        category_id=mapping.category_id,
        income_treatment=mapping.income_treatment.value if mapping.income_treatment else None,
        expense_treatment=(mapping.expense_treatment.value if mapping.expense_treatment else None),
        vat_treatment=mapping.vat_treatment.value,
        deductibility_percentage=mapping.deductibility_percentage.value,
        vat_creditable_percentage=mapping.vat_creditable_percentage.value,
        requires_cfdi=mapping.requires_cfdi,
        requires_payment_evidence=mapping.requires_payment_evidence,
    )


@router.get(
    "/{organization_id}/taxes/mx/category-mappings",
    response_model=list[MexicoCategoryMappingResponse],
    summary="List Mexico category mappings",
)
def list_mappings(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListMexicoCategoryMappingsQuery, Depends(get_list_mappings_query)],
    tax_profile_id: Annotated[UUID, Query()],
) -> list[MexicoCategoryMappingResponse]:
    items = query.execute(organization_id, tax_profile_id)
    return [
        MexicoCategoryMappingResponse(
            id=item.id,
            tax_profile_id=item.tax_profile_id,
            category_id=item.category_id,
            income_treatment=item.income_treatment.value if item.income_treatment else None,
            expense_treatment=(item.expense_treatment.value if item.expense_treatment else None),
            vat_treatment=item.vat_treatment.value,
            deductibility_percentage=item.deductibility_percentage.value,
            vat_creditable_percentage=item.vat_creditable_percentage.value,
            requires_cfdi=item.requires_cfdi,
            requires_payment_evidence=item.requires_payment_evidence,
        )
        for item in items
    ]


@router.patch(
    "/{organization_id}/taxes/mx/category-mappings/{mapping_id}",
    response_model=MexicoCategoryMappingResponse,
    summary="Update Mexico category mapping",
)
def update_mapping(
    organization_id: UUID,
    mapping_id: UUID,
    payload: MexicoCategoryMappingUpdate,
    _membership: RequireManager,
    command: Annotated[UpdateMexicoTaxCategoryMappingCommand, Depends(get_update_mapping_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> MexicoCategoryMappingResponse:
    fields = frozenset(payload.model_fields_set)
    try:
        with uow:
            mapping = command.execute(
                UpdateMexicoTaxCategoryMappingInput(
                    organization_id=organization_id,
                    mapping_id=mapping_id,
                    fields_set=fields,
                    vat_treatment=payload.vat_treatment,
                    income_treatment=payload.income_treatment,
                    expense_treatment=payload.expense_treatment,
                    deductibility_percentage=payload.deductibility_percentage,
                    vat_creditable_percentage=payload.vat_creditable_percentage,
                    requires_cfdi=payload.requires_cfdi,
                    requires_payment_evidence=payload.requires_payment_evidence,
                    clear_income_treatment=(
                        "income_treatment" in fields and payload.income_treatment is None
                    ),
                    clear_expense_treatment=(
                        "expense_treatment" in fields and payload.expense_treatment is None
                    ),
                )
            )
            uow.commit()
    except TaxMxError as exc:
        raise _http_map(exc) from exc
    return MexicoCategoryMappingResponse(
        id=mapping.id,
        tax_profile_id=mapping.tax_profile_id,
        category_id=mapping.category_id,
        income_treatment=mapping.income_treatment.value if mapping.income_treatment else None,
        expense_treatment=(mapping.expense_treatment.value if mapping.expense_treatment else None),
        vat_treatment=mapping.vat_treatment.value,
        deductibility_percentage=mapping.deductibility_percentage.value,
        vat_creditable_percentage=mapping.vat_creditable_percentage.value,
        requires_cfdi=mapping.requires_cfdi,
        requires_payment_evidence=mapping.requires_payment_evidence,
    )


@router.post(
    "/{organization_id}/taxes/mx/transactions/{transaction_id}/classification",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Classify Mexico tax transaction",
)
def classify_transaction(
    organization_id: UUID,
    transaction_id: UUID,
    payload: MexicoClassificationCreate,
    current_user: CurrentUser,
    _membership: RequireWriter,
    command: Annotated[ClassifyMexicoTaxTransactionCommand, Depends(get_classify_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> dict:
    try:
        with uow:
            override = command.execute(
                ClassifyMexicoTaxTransactionInput(
                    organization_id=organization_id,
                    tax_profile_id=payload.tax_profile_id,
                    transaction_id=transaction_id,
                    vat_treatment=payload.vat_treatment,
                    created_by_user_id=current_user.id,
                    income_treatment=payload.income_treatment,
                    expense_treatment=payload.expense_treatment,
                    deductibility_percentage=payload.deductibility_percentage,
                    vat_creditable_percentage=payload.vat_creditable_percentage,
                    requires_cfdi=payload.requires_cfdi,
                    reason=payload.reason,
                )
            )
            uow.commit()
    except TaxMxError as exc:
        raise _http_map(exc) from exc
    return {"id": str(override.id), "transaction_id": str(override.transaction_id)}


@router.get(
    "/{organization_id}/taxes/mx/transactions/unclassified",
    response_model=UnclassifiedTransactionListResponse,
    summary="List unclassified Mexico tax transactions",
)
def list_unclassified(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListUnclassifiedTaxTransactionsQuery, Depends(get_unclassified_query)],
    tax_profile_id: Annotated[UUID, Query()],
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    transaction_type: Annotated[str | None, Query()] = None,
    category_id: Annotated[UUID | None, Query()] = None,
    account_id: Annotated[UUID | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> UnclassifiedTransactionListResponse:
    items, total = query.execute(
        organization_id,
        tax_profile_id,
        date_from=date_from,
        date_to=date_to,
        transaction_type=transaction_type,
        category_id=category_id,
        account_id=account_id,
        limit=limit,
        offset=offset,
    )
    return UnclassifiedTransactionListResponse(
        items=[
            UnclassifiedTransactionItem(
                transaction_id=item.transaction_id,
                description=item.description,
                occurred_at=item.occurred_on,
                amount=item.amount,
                currency=item.currency,
                category=(
                    {"id": str(item.category_id), "name": None} if item.category_id else None
                ),
                missing=["expense_treatment", "vat_treatment"]
                if item.transaction_type == "expense"
                else ["income_treatment", "vat_treatment"],
            )
            for item in items
        ],
        total=total,
    )


@router.post(
    "/{organization_id}/taxes/mx/periods/{period_id}/calculate",
    response_model=MexicoWorkpaperResponse,
    summary="Calculate Mexico tax period workpaper",
    description=MX_DESCRIPTION,
)
def calculate_period(
    organization_id: UUID,
    period_id: UUID,
    current_user: CurrentUser,
    _membership: RequireWriter,
    command: Annotated[CalculateMexicoTaxPeriodCommand, Depends(get_calculate_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> MexicoWorkpaperResponse:
    try:
        with uow:
            result = command.execute(organization_id, period_id, current_user.id)
            uow.commit()
    except TaxMxError as exc:
        raise _http_map(exc) from exc
    wp = result.workpaper
    return MexicoWorkpaperResponse(
        period_id=wp.period_id,
        currency=wp.currency,
        income={
            "collected": str(wp.collected_income),
            "taxable": str(wp.taxable_income),
            "exempt": str(wp.exempt_income),
        },
        expenses={
            "paid": str(wp.paid_expenses),
            "deductible": str(wp.deductible_expenses),
            "non_deductible": str(wp.non_deductible_expenses),
        },
        vat={
            "output": str(wp.output_vat),
            "identified_input": str(wp.identified_input_vat),
            "creditable": str(wp.creditable_vat),
            "withheld": str(wp.withheld_vat),
            "due": str(wp.vat_due),
            "credit_balance": str(wp.vat_credit_balance),
        },
        income_tax={
            "estimated_before_withholdings": str(wp.estimated_income_tax),
            "withheld": str(wp.withheld_income_tax),
            "due": str(wp.income_tax_due),
        },
        estimated_total_due=wp.estimated_total_due,
        quality={
            "classified_transactions": wp.quality.classified_transactions,
            "unclassified_transactions": wp.quality.unclassified_transactions,
            "missing_evidence": wp.quality.missing_evidence,
            "mismatched_evidence": wp.quality.mismatched_evidence,
            "completeness_percentage": str(wp.quality.completeness_percentage),
        },
        warnings=[
            {
                "code": warning.code,
                "message": warning.message,
                "transaction_id": str(warning.transaction_id) if warning.transaction_id else None,
            }
            for warning in wp.warnings
        ],
        version=result.version,
    )


@router.get(
    "/{organization_id}/taxes/mx/periods/{period_id}/workpaper",
    response_model=MexicoWorkpaperResponse,
    summary="Get Mexico tax workpaper",
    description=MX_DESCRIPTION,
)
def get_workpaper(
    organization_id: UUID,
    period_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetMexicoTaxWorkpaperQuery, Depends(get_workpaper_query)],
) -> MexicoWorkpaperResponse:
    try:
        payload = query.execute(organization_id, period_id)
    except TaxMxError as exc:
        raise _http_map(exc) from exc
    return MexicoWorkpaperResponse(
        period_id=UUID(str(payload["period_id"])),
        currency=payload["currency"],
        income=payload["income"],
        expenses=payload["expenses"],
        vat=payload["vat"],
        income_tax=payload["income_tax"],
        estimated_total_due=payload["estimated_total_due"],
        quality=payload["quality"],
        warnings=payload.get("warnings", []),
        is_stale=payload.get("is_stale", False),
        version=payload.get("version"),
    )


@router.get(
    "/{organization_id}/taxes/mx/summary",
    response_model=MexicoTaxSummaryResponse,
    summary="Mexico tax reserve summary",
    description=MX_DESCRIPTION,
)
def get_summary(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetMexicoTaxSummaryQuery, Depends(get_summary_query)],
) -> MexicoTaxSummaryResponse:
    return MexicoTaxSummaryResponse(**query.execute(organization_id))
