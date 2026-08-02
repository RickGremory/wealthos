"""HTTP routes for Recurring under organizations."""

from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from wealthos.core.security.current_user import CurrentUser
from wealthos.core.security.organization_access import OrganizationMember
from wealthos.core.security.organization_permissions import require_organization_role
from wealthos.modules.recurring.api.dependencies import (
    get_archive_handler,
    get_create_exception_handler,
    get_create_rule_handler,
    get_create_version_handler,
    get_deactivate_exception_handler,
    get_end_handler,
    get_get_rule_query,
    get_list_occurrences_query,
    get_list_rules_query,
    get_org_timezone,
    get_pause_handler,
    get_preview_rule_query,
    get_preview_unsaved_query,
    get_resume_handler,
    get_unit_of_work,
    get_update_metadata_handler,
)
from wealthos.modules.recurring.api.exception_mapping import http_map_recurring_errors
from wealthos.modules.recurring.api.pattern_mapping import pattern_from_schema
from wealthos.modules.recurring.api.schemas import (
    ArchiveRequest,
    CreateExceptionRequest,
    CreateRecurringRuleRequest,
    CreateVersionRequest,
    EndRequest,
    PauseRequest,
    PreviewRuleRequest,
    PreviewUnsavedRequest,
    RecurringOccurrenceResponse,
    RecurringPreviewResponse,
    RecurringRuleDetailResponse,
    RecurringRuleListItemResponse,
    RecurringVersionResponse,
    ResumeRequest,
    UpdateMetadataRequest,
)
from wealthos.modules.recurring.application.commands.create_exception import (
    CreateRecurringOccurrenceExceptionCommand,
    CreateRecurringOccurrenceExceptionHandler,
    DeactivateRecurringOccurrenceExceptionCommand,
    DeactivateRecurringOccurrenceExceptionHandler,
)
from wealthos.modules.recurring.application.commands.create_rule import (
    CreateRecurringRuleCommand,
    CreateRecurringRuleHandler,
)
from wealthos.modules.recurring.application.commands.create_rule_version import (
    CreateRecurringRuleVersionCommand,
    CreateRecurringRuleVersionHandler,
    RecurringVersionChanges,
)
from wealthos.modules.recurring.application.commands.end_archive_rule import (
    ArchiveRecurringRuleCommand,
    ArchiveRecurringRuleHandler,
    EndRecurringRuleCommand,
    EndRecurringRuleHandler,
)
from wealthos.modules.recurring.application.commands.pause_resume_rule import (
    PauseRecurringRuleCommand,
    PauseRecurringRuleHandler,
    ResumeRecurringRuleCommand,
    ResumeRecurringRuleHandler,
)
from wealthos.modules.recurring.application.commands.update_metadata import (
    UpdateRecurringRuleMetadataCommand,
    UpdateRecurringRuleMetadataHandler,
)
from wealthos.modules.recurring.application.dto.views import (
    RecurringOccurrenceDTO,
    RecurringRuleDetailDTO,
    RecurringRuleListDTO,
    RecurringVersionDTO,
)
from wealthos.modules.recurring.application.queries.list_get_rules import (
    GetRecurringRuleInput,
    GetRecurringRuleQuery,
    ListRecurringRulesInput,
    ListRecurringRulesQuery,
)
from wealthos.modules.recurring.application.queries.preview_occurrences import (
    ListRecurringOccurrencesInput,
    ListRecurringOccurrencesQuery,
    PreviewRecurringRuleInput,
    PreviewRecurringRuleQuery,
    PreviewUnsavedRecurringRuleInput,
    PreviewUnsavedRecurringRuleQuery,
)
from wealthos.modules.recurring.domain.enums.occurrence import (
    RecurringExceptionType,
    RecurringSettlementMode,
)
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringAmountStrategy,
    RecurringCertainty,
    RecurringDirection,
    RecurringRuleStatus,
    RecurringSourceType,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

router = APIRouter(prefix="/{organization_id}/recurring", tags=["Recurring"])


def _occ(dto: RecurringOccurrenceDTO) -> RecurringOccurrenceResponse:
    return RecurringOccurrenceResponse.model_validate(dto, from_attributes=True)


def _version(dto: RecurringVersionDTO) -> RecurringVersionResponse:
    return RecurringVersionResponse(
        id=dto.id,
        effective_from=dto.effective_from,
        effective_until=dto.effective_until,
        name=dto.name,
        direction=dto.direction,
        amount=dto.amount,
        currency=dto.currency,
        frequency=dto.frequency,
        interval=dto.interval,
        day_of_month=dto.day_of_month,
        end_of_month=dto.end_of_month,
        days_of_week=list(dto.days_of_week),
        month_of_year=dto.month_of_year,
        invalid_date_policy=dto.invalid_date_policy,
        starts_on=dto.starts_on,
        ends_on=dto.ends_on,
        grace_period_days=dto.grace_period_days,
        amount_strategy=dto.amount_strategy,
        certainty=dto.certainty,
        settlement_mode=dto.settlement_mode,
        account_id=dto.account_id,
        destination_account_id=dto.destination_account_id,
        category_id=dto.category_id,
        notes=dto.notes,
    )


def _list_item(dto: RecurringRuleListDTO) -> RecurringRuleListItemResponse:
    return RecurringRuleListItemResponse(
        id=dto.id,
        name=dto.name,
        direction=dto.direction,
        amount=dto.amount,
        currency=dto.currency,
        status=dto.status,
        source_type=dto.source_type,
        is_managed_externally=dto.is_managed_externally,
        frequency=dto.frequency,
        interval=dto.interval,
        schedule_label=dto.schedule_label,
        version=dto.version,
        next_occurrence=_occ(dto.next_occurrence) if dto.next_occurrence else None,
    )


def _detail(dto: RecurringRuleDetailDTO) -> RecurringRuleDetailResponse:
    return RecurringRuleDetailResponse(
        id=dto.id,
        name=dto.name,
        direction=dto.direction,
        amount=dto.amount,
        currency=dto.currency,
        status=dto.status,
        source_type=dto.source_type,
        is_managed_externally=dto.is_managed_externally,
        related_resource_type=dto.related_resource_type,
        related_resource_id=dto.related_resource_id,
        version=dto.version,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        archived_at=dto.archived_at,
        current_version=_version(dto.current_version),
        versions=[_version(item) for item in dto.versions],
        upcoming_occurrences=[_occ(item) for item in dto.upcoming_occurrences],
        notes=dto.notes,
    )


@router.get("", response_model=list[RecurringRuleListItemResponse])
def list_rules(
    organization_id: UUID,
    _: OrganizationMember,
    query: Annotated[ListRecurringRulesQuery, Depends(get_list_rules_query)],
    timezone: Annotated[str, Depends(get_org_timezone)],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    direction: str | None = None,
    currency: str | None = None,
    source_type: str | None = None,
    include_archived: bool = False,
    evaluated_on: date | None = None,
) -> list[RecurringRuleListItemResponse]:
    with http_map_recurring_errors():
        items = query.execute(
            ListRecurringRulesInput(
                organization_id=organization_id,
                evaluated_on=evaluated_on or date.today(),
                timezone=timezone,
                status=RecurringRuleStatus.parse(status_filter) if status_filter else None,
                direction=RecurringDirection.parse(direction) if direction else None,
                currency=currency.upper() if currency else None,
                source_type=(
                    RecurringSourceType.parse(source_type) if source_type else None
                ),
                include_archived=include_archived,
            )
        )
    return [_list_item(item) for item in items]


@router.post(
    "",
    response_model=RecurringRuleDetailResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_organization_role("owner", "admin", "member"))],
)
def create_rule(
    organization_id: UUID,
    payload: CreateRecurringRuleRequest,
    _: OrganizationMember,
    current_user: CurrentUser,
    handler: Annotated[CreateRecurringRuleHandler, Depends(get_create_rule_handler)],
    get_query: Annotated[GetRecurringRuleQuery, Depends(get_get_rule_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
    timezone: Annotated[str, Depends(get_org_timezone)],
) -> RecurringRuleDetailResponse:
    with http_map_recurring_errors():
        aggregate = handler.execute(
            CreateRecurringRuleCommand(
                organization_id=organization_id,
                actor_id=current_user.id,
                name=payload.name,
                direction=RecurringDirection.parse(payload.direction),
                amount=payload.amount,
                currency=payload.currency,
                pattern=pattern_from_schema(payload.pattern),
                starts_on=payload.starts_on,
                ends_on=payload.ends_on,
                amount_strategy=RecurringAmountStrategy.parse(payload.amount_strategy),
                certainty=RecurringCertainty.parse(payload.certainty),
                settlement_mode=RecurringSettlementMode.parse(payload.settlement_mode),
                account_id=payload.account_id,
                destination_account_id=payload.destination_account_id,
                category_id=payload.category_id,
                grace_period_days=payload.grace_period_days,
                notes=payload.notes,
            )
        )
        uow.commit()
        detail = get_query.execute(
            GetRecurringRuleInput(
                organization_id=organization_id,
                rule_id=aggregate.id,
                evaluated_on=date.today(),
                timezone=timezone,
            )
        )
    return _detail(detail)


@router.post("/preview", response_model=RecurringPreviewResponse)
def preview_unsaved(
    organization_id: UUID,
    payload: PreviewUnsavedRequest,
    _: OrganizationMember,
    query: Annotated[PreviewUnsavedRecurringRuleQuery, Depends(get_preview_unsaved_query)],
    timezone: Annotated[str, Depends(get_org_timezone)],
) -> RecurringPreviewResponse:
    with http_map_recurring_errors():
        result = query.execute(
            PreviewUnsavedRecurringRuleInput(
                organization_id=organization_id,
                period_start=payload.from_date,
                period_end=payload.to_date,
                evaluated_on=date.today(),
                timezone=payload.timezone or timezone,
                name=payload.name,
                direction=RecurringDirection.parse(payload.direction),
                amount=payload.amount,
                currency=payload.currency,
                pattern=pattern_from_schema(payload.pattern),
                starts_on=payload.starts_on,
                ends_on=payload.ends_on,
                amount_strategy=RecurringAmountStrategy.parse(payload.amount_strategy),
                certainty=RecurringCertainty.parse(payload.certainty),
                grace_period_days=payload.grace_period_days,
            )
        )
    return RecurringPreviewResponse(
        dates=list(result.dates),
        occurrences=[_occ(item) for item in result.occurrences],
    )


@router.get("/occurrences", response_model=list[RecurringOccurrenceResponse])
def list_occurrences(
    organization_id: UUID,
    _: OrganizationMember,
    query: Annotated[ListRecurringOccurrencesQuery, Depends(get_list_occurrences_query)],
    timezone: Annotated[str, Depends(get_org_timezone)],
    from_date: Annotated[date, Query(alias="from")],
    to_date: Annotated[date, Query(alias="to")],
    currency: str | None = None,
    status: Annotated[str | None, Query()] = None,
    rule_id: UUID | None = None,
    evaluated_on: date | None = None,
) -> list[RecurringOccurrenceResponse]:
    statuses = tuple(part.strip() for part in status.split(",")) if status else ()
    with http_map_recurring_errors():
        items = query.execute(
            ListRecurringOccurrencesInput(
                organization_id=organization_id,
                period_start=from_date,
                period_end=to_date,
                evaluated_on=evaluated_on or date.today(),
                timezone=timezone,
                currency=currency.upper() if currency else None,
                rule_id=rule_id,
                statuses=statuses,
            )
        )
    return [_occ(item) for item in items]


@router.get("/{rule_id}", response_model=RecurringRuleDetailResponse)
def get_rule(
    organization_id: UUID,
    rule_id: UUID,
    _: OrganizationMember,
    query: Annotated[GetRecurringRuleQuery, Depends(get_get_rule_query)],
    timezone: Annotated[str, Depends(get_org_timezone)],
    evaluated_on: date | None = None,
) -> RecurringRuleDetailResponse:
    with http_map_recurring_errors():
        detail = query.execute(
            GetRecurringRuleInput(
                organization_id=organization_id,
                rule_id=rule_id,
                evaluated_on=evaluated_on or date.today(),
                timezone=timezone,
            )
        )
    return _detail(detail)


@router.post("/{rule_id}/preview", response_model=RecurringPreviewResponse)
def preview_rule(
    organization_id: UUID,
    rule_id: UUID,
    payload: PreviewRuleRequest,
    _: OrganizationMember,
    query: Annotated[PreviewRecurringRuleQuery, Depends(get_preview_rule_query)],
    timezone: Annotated[str, Depends(get_org_timezone)],
) -> RecurringPreviewResponse:
    with http_map_recurring_errors():
        result = query.execute(
            PreviewRecurringRuleInput(
                organization_id=organization_id,
                rule_id=rule_id,
                period_start=payload.from_date,
                period_end=payload.to_date,
                evaluated_on=date.today(),
                timezone=payload.timezone or timezone,
            )
        )
    return RecurringPreviewResponse(
        dates=list(result.dates),
        occurrences=[_occ(item) for item in result.occurrences],
    )


@router.patch(
    "/{rule_id}/metadata",
    response_model=RecurringRuleDetailResponse,
    dependencies=[Depends(require_organization_role("owner", "admin", "member"))],
)
def update_metadata(
    organization_id: UUID,
    rule_id: UUID,
    payload: UpdateMetadataRequest,
    _: OrganizationMember,
    current_user: CurrentUser,
    handler: Annotated[
        UpdateRecurringRuleMetadataHandler,
        Depends(get_update_metadata_handler),
    ],
    get_query: Annotated[GetRecurringRuleQuery, Depends(get_get_rule_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
    timezone: Annotated[str, Depends(get_org_timezone)],
) -> RecurringRuleDetailResponse:
    with http_map_recurring_errors():
        handler.execute(
            UpdateRecurringRuleMetadataCommand(
                organization_id=organization_id,
                actor_id=current_user.id,
                rule_id=rule_id,
                expected_version=payload.expected_version,
                notes=payload.notes,
            )
        )
        uow.commit()
        detail = get_query.execute(
            GetRecurringRuleInput(
                organization_id=organization_id,
                rule_id=rule_id,
                evaluated_on=date.today(),
                timezone=timezone,
            )
        )
    return _detail(detail)


@router.post(
    "/{rule_id}/versions",
    response_model=RecurringRuleDetailResponse,
    dependencies=[Depends(require_organization_role("owner", "admin", "member"))],
)
def create_version(
    organization_id: UUID,
    rule_id: UUID,
    payload: CreateVersionRequest,
    _: OrganizationMember,
    current_user: CurrentUser,
    handler: Annotated[
        CreateRecurringRuleVersionHandler,
        Depends(get_create_version_handler),
    ],
    get_query: Annotated[GetRecurringRuleQuery, Depends(get_get_rule_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
    timezone: Annotated[str, Depends(get_org_timezone)],
) -> RecurringRuleDetailResponse:
    with http_map_recurring_errors():
        handler.execute(
            CreateRecurringRuleVersionCommand(
                organization_id=organization_id,
                actor_id=current_user.id,
                rule_id=rule_id,
                effective_from=payload.effective_from,
                expected_version=payload.expected_version,
                today=date.today(),
                changes=RecurringVersionChanges(
                    name=payload.name,
                    direction=RecurringDirection.parse(payload.direction),
                    amount=payload.amount,
                    currency=payload.currency,
                    pattern=pattern_from_schema(payload.pattern),
                    starts_on=payload.starts_on,
                    ends_on=payload.ends_on,
                    amount_strategy=RecurringAmountStrategy.parse(payload.amount_strategy),
                    certainty=RecurringCertainty.parse(payload.certainty),
                    settlement_mode=RecurringSettlementMode.parse(payload.settlement_mode),
                    account_id=payload.account_id,
                    destination_account_id=payload.destination_account_id,
                    category_id=payload.category_id,
                    grace_period_days=payload.grace_period_days,
                    notes=payload.notes,
                ),
            )
        )
        uow.commit()
        detail = get_query.execute(
            GetRecurringRuleInput(
                organization_id=organization_id,
                rule_id=rule_id,
                evaluated_on=date.today(),
                timezone=timezone,
            )
        )
    return _detail(detail)


@router.post(
    "/{rule_id}/pauses",
    response_model=RecurringRuleDetailResponse,
    dependencies=[Depends(require_organization_role("owner", "admin", "member"))],
)
def pause_rule(
    organization_id: UUID,
    rule_id: UUID,
    payload: PauseRequest,
    _: OrganizationMember,
    current_user: CurrentUser,
    handler: Annotated[PauseRecurringRuleHandler, Depends(get_pause_handler)],
    get_query: Annotated[GetRecurringRuleQuery, Depends(get_get_rule_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
    timezone: Annotated[str, Depends(get_org_timezone)],
) -> RecurringRuleDetailResponse:
    with http_map_recurring_errors():
        handler.execute(
            PauseRecurringRuleCommand(
                organization_id=organization_id,
                actor_id=current_user.id,
                rule_id=rule_id,
                starts_on=payload.starts_on,
                ends_on=payload.ends_on,
                expected_version=payload.expected_version,
                reason=payload.reason,
            )
        )
        uow.commit()
        detail = get_query.execute(
            GetRecurringRuleInput(
                organization_id=organization_id,
                rule_id=rule_id,
                evaluated_on=date.today(),
                timezone=timezone,
            )
        )
    return _detail(detail)


@router.post(
    "/{rule_id}/resume",
    response_model=RecurringRuleDetailResponse,
    dependencies=[Depends(require_organization_role("owner", "admin", "member"))],
)
def resume_rule(
    organization_id: UUID,
    rule_id: UUID,
    payload: ResumeRequest,
    _: OrganizationMember,
    current_user: CurrentUser,
    handler: Annotated[ResumeRecurringRuleHandler, Depends(get_resume_handler)],
    get_query: Annotated[GetRecurringRuleQuery, Depends(get_get_rule_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
    timezone: Annotated[str, Depends(get_org_timezone)],
) -> RecurringRuleDetailResponse:
    with http_map_recurring_errors():
        handler.execute(
            ResumeRecurringRuleCommand(
                organization_id=organization_id,
                actor_id=current_user.id,
                rule_id=rule_id,
                resume_on=payload.resume_on,
                expected_version=payload.expected_version,
            )
        )
        uow.commit()
        detail = get_query.execute(
            GetRecurringRuleInput(
                organization_id=organization_id,
                rule_id=rule_id,
                evaluated_on=date.today(),
                timezone=timezone,
            )
        )
    return _detail(detail)


@router.post(
    "/{rule_id}/end",
    response_model=RecurringRuleDetailResponse,
    dependencies=[Depends(require_organization_role("owner", "admin"))],
)
def end_rule(
    organization_id: UUID,
    rule_id: UUID,
    payload: EndRequest,
    _: OrganizationMember,
    current_user: CurrentUser,
    handler: Annotated[EndRecurringRuleHandler, Depends(get_end_handler)],
    get_query: Annotated[GetRecurringRuleQuery, Depends(get_get_rule_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
    timezone: Annotated[str, Depends(get_org_timezone)],
) -> RecurringRuleDetailResponse:
    with http_map_recurring_errors():
        handler.execute(
            EndRecurringRuleCommand(
                organization_id=organization_id,
                actor_id=current_user.id,
                rule_id=rule_id,
                ends_on=payload.ends_on,
                expected_version=payload.expected_version,
                today=date.today(),
            )
        )
        uow.commit()
        detail = get_query.execute(
            GetRecurringRuleInput(
                organization_id=organization_id,
                rule_id=rule_id,
                evaluated_on=date.today(),
                timezone=timezone,
            )
        )
    return _detail(detail)


@router.post(
    "/{rule_id}/archive",
    response_model=RecurringRuleDetailResponse,
    dependencies=[Depends(require_organization_role("owner", "admin"))],
)
def archive_rule(
    organization_id: UUID,
    rule_id: UUID,
    payload: ArchiveRequest,
    _: OrganizationMember,
    current_user: CurrentUser,
    handler: Annotated[ArchiveRecurringRuleHandler, Depends(get_archive_handler)],
    get_query: Annotated[GetRecurringRuleQuery, Depends(get_get_rule_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
    timezone: Annotated[str, Depends(get_org_timezone)],
) -> RecurringRuleDetailResponse:
    with http_map_recurring_errors():
        handler.execute(
            ArchiveRecurringRuleCommand(
                organization_id=organization_id,
                actor_id=current_user.id,
                rule_id=rule_id,
                expected_version=payload.expected_version,
            )
        )
        uow.commit()
        detail = get_query.execute(
            GetRecurringRuleInput(
                organization_id=organization_id,
                rule_id=rule_id,
                evaluated_on=date.today(),
                timezone=timezone,
            )
        )
    return _detail(detail)


@router.post(
    "/{rule_id}/exceptions",
    response_model=RecurringRuleDetailResponse,
    dependencies=[Depends(require_organization_role("owner", "admin", "member"))],
)
def create_exception(
    organization_id: UUID,
    rule_id: UUID,
    payload: CreateExceptionRequest,
    _: OrganizationMember,
    current_user: CurrentUser,
    handler: Annotated[
        CreateRecurringOccurrenceExceptionHandler,
        Depends(get_create_exception_handler),
    ],
    get_query: Annotated[GetRecurringRuleQuery, Depends(get_get_rule_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
    timezone: Annotated[str, Depends(get_org_timezone)],
) -> RecurringRuleDetailResponse:
    with http_map_recurring_errors():
        handler.execute(
            CreateRecurringOccurrenceExceptionCommand(
                organization_id=organization_id,
                actor_id=current_user.id,
                rule_id=rule_id,
                occurrence_key=payload.occurrence_key,
                exception_type=RecurringExceptionType.parse(payload.exception_type),
                expected_version=payload.expected_version,
                evaluated_on=date.today(),
                timezone=timezone,
                replacement_expected_on=payload.replacement_expected_on,
                replacement_amount=payload.replacement_amount,
                replacement_certainty=(
                    RecurringCertainty.parse(payload.replacement_certainty)
                    if payload.replacement_certainty
                    else None
                ),
                reason=payload.reason,
            )
        )
        uow.commit()
        detail = get_query.execute(
            GetRecurringRuleInput(
                organization_id=organization_id,
                rule_id=rule_id,
                evaluated_on=date.today(),
                timezone=timezone,
            )
        )
    return _detail(detail)


@router.post(
    "/{rule_id}/exceptions/{exception_id}/deactivate",
    response_model=RecurringRuleDetailResponse,
    dependencies=[Depends(require_organization_role("owner", "admin", "member"))],
)
def deactivate_exception(
    organization_id: UUID,
    rule_id: UUID,
    exception_id: UUID,
    payload: ArchiveRequest,
    _: OrganizationMember,
    current_user: CurrentUser,
    handler: Annotated[
        DeactivateRecurringOccurrenceExceptionHandler,
        Depends(get_deactivate_exception_handler),
    ],
    get_query: Annotated[GetRecurringRuleQuery, Depends(get_get_rule_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
    timezone: Annotated[str, Depends(get_org_timezone)],
) -> RecurringRuleDetailResponse:
    with http_map_recurring_errors():
        handler.execute(
            DeactivateRecurringOccurrenceExceptionCommand(
                organization_id=organization_id,
                actor_id=current_user.id,
                rule_id=rule_id,
                exception_id=exception_id,
                expected_version=payload.expected_version,
            )
        )
        uow.commit()
        detail = get_query.execute(
            GetRecurringRuleInput(
                organization_id=organization_id,
                rule_id=rule_id,
                evaluated_on=date.today(),
                timezone=timezone,
            )
        )
    return _detail(detail)
