"""HTTP routes for legal documents and consents."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from wealthos.core.security.current_user import CurrentUser
from wealthos.modules.legal.api.dependencies import (
    get_legal_consent_service,
    get_unit_of_work,
)
from wealthos.modules.legal.application.services.legal_consent_service import (
    ConsentContext,
    LegalAcceptanceItem,
    LegalConsentService,
)
from wealthos.modules.legal.domain.exceptions import (
    InvalidLegalAcceptance,
    LegalAcceptanceRequired,
    LegalDocumentNotFound,
    LegalDocumentVersionOutdated,
    LegalError,
)
from wealthos.modules.legal.domain.value_objects.document_types import (
    SOURCE_FORCED_REACCEPTANCE,
    SOURCE_SETTINGS,
)
from wealthos.modules.legal.schemas.responses import (
    AcceptDocumentsRequest,
    ComplianceStatusResponse,
    LegalDocumentResponse,
    MarketingConsentRequest,
    MarketingConsentState,
    PendingDocumentResponse,
    RegistrationRequirementsResponse,
    UserDocumentsResponse,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

router = APIRouter()


def _client_context(request: Request, *, source: str) -> ConsentContext:
    forwarded = request.headers.get("x-forwarded-for")
    ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else None)
    return ConsentContext(
        ip_address=ip,
        user_agent=request.headers.get("user-agent"),
        source=source,
    )


def _http_map(exc: Exception) -> HTTPException:
    if isinstance(exc, LegalDocumentNotFound):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, LegalDocumentVersionOutdated):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": exc.code, "message": str(exc)},
        )
    if isinstance(exc, LegalAcceptanceRequired):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": exc.code, "message": str(exc)},
        )
    if isinstance(exc, InvalidLegalAcceptance):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    if isinstance(exc, LegalError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/registration-requirements",
    response_model=RegistrationRequirementsResponse,
    summary="Documents required at registration",
)
def registration_requirements(
    service: Annotated[LegalConsentService, Depends(get_legal_consent_service)],
) -> RegistrationRequirementsResponse:
    try:
        return RegistrationRequirementsResponse.model_validate(
            service.registration_requirements()
        )
    except LegalError as exc:
        raise _http_map(exc) from exc


@router.get(
    "/documents/{document_type}",
    response_model=LegalDocumentResponse,
    summary="Active legal document by type",
)
def get_document(
    document_type: str,
    service: Annotated[LegalConsentService, Depends(get_legal_consent_service)],
) -> LegalDocumentResponse:
    try:
        doc = service.get_active_document(document_type)
    except LegalError as exc:
        raise _http_map(exc) from exc
    return LegalDocumentResponse(
        type=doc.document_type,
        version=doc.version,
        title=doc.title,
        url=doc.content_url,
        content_markdown=doc.content_markdown,
        effective_at=doc.effective_at,
        published_at=doc.published_at,
        requires_reacceptance=doc.requires_reacceptance,
        change_summary=doc.change_summary,
    )


@router.get(
    "/me/status",
    response_model=ComplianceStatusResponse,
    summary="Current user legal compliance status",
)
def me_status(
    current_user: CurrentUser,
    service: Annotated[LegalConsentService, Depends(get_legal_consent_service)],
) -> ComplianceStatusResponse:
    status_result = service.get_compliance_status(current_user.id)
    return ComplianceStatusResponse(
        is_compliant=status_result.is_compliant,
        pending_documents=[
            PendingDocumentResponse(
                type=p.document_type,
                version=p.version,
                title=p.title,
                url=p.url,
            )
            for p in status_result.pending_documents
        ],
    )


@router.post(
    "/me/acceptances",
    response_model=ComplianceStatusResponse,
    summary="Record acceptances for pending legal documents",
)
def me_acceptances(
    payload: AcceptDocumentsRequest,
    request: Request,
    current_user: CurrentUser,
    service: Annotated[LegalConsentService, Depends(get_legal_consent_service)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> ComplianceStatusResponse:
    items = [
        LegalAcceptanceItem(
            document_type=item.document_type,
            version=item.version,
            accepted=item.accepted,
            acknowledged=item.acknowledged,
        )
        for item in payload.acceptances
    ]
    try:
        with uow:
            result = service.record_acceptances(
                user_id=current_user.id,
                acceptances=items,
                context=_client_context(request, source=SOURCE_FORCED_REACCEPTANCE),
            )
            uow.commit()
    except LegalError as exc:
        raise _http_map(exc) from exc

    return ComplianceStatusResponse(
        is_compliant=result.is_compliant,
        pending_documents=[
            PendingDocumentResponse(
                type=p.document_type,
                version=p.version,
                title=p.title,
                url=p.url,
            )
            for p in result.pending_documents
        ],
    )


@router.get(
    "/me/documents",
    response_model=UserDocumentsResponse,
    summary="Accepted documents and marketing consent for settings",
)
def me_documents(
    current_user: CurrentUser,
    service: Annotated[LegalConsentService, Depends(get_legal_consent_service)],
) -> UserDocumentsResponse:
    return UserDocumentsResponse.model_validate(service.list_user_documents(current_user.id))


@router.post(
    "/me/marketing-consent",
    response_model=MarketingConsentState,
    summary="Accept or withdraw marketing consent",
)
def me_marketing_consent(
    payload: MarketingConsentRequest,
    request: Request,
    current_user: CurrentUser,
    service: Annotated[LegalConsentService, Depends(get_legal_consent_service)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> MarketingConsentState:
    try:
        with uow:
            result = service.set_marketing_consent(
                user_id=current_user.id,
                accepted=payload.accepted,
                context=_client_context(request, source=SOURCE_SETTINGS),
            )
            uow.commit()
    except LegalError as exc:
        raise _http_map(exc) from exc
    return MarketingConsentState.model_validate(result)
