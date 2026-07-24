"""Authentication HTTP routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from wealthos.core.security.current_user import CurrentUser
from wealthos.modules.identity.api.dependencies import (
    get_login_user_command,
    get_register_user_command,
    get_unit_of_work,
)
from wealthos.modules.identity.application.commands.login_user import (
    LoginUserCommand,
    LoginUserInput,
)
from wealthos.modules.identity.application.commands.register_user import (
    RegisterUserCommand,
    RegisterUserInput,
)
from wealthos.modules.identity.domain.exceptions import (
    DisplayNameEmpty,
    DisplayNameTooLong,
    IdentityError,
    InactiveUser,
    InvalidCredentials,
    InvalidEmail,
    UserEmailAlreadyExists,
    WeakPassword,
)
from wealthos.modules.identity.schemas.auth import RegisterRequest, TokenResponse
from wealthos.modules.identity.schemas.current_user import CurrentUserResponse
from wealthos.modules.legal.application.services.legal_consent_service import (
    LegalAcceptanceItem,
)
from wealthos.modules.legal.domain.exceptions import (
    LegalAcceptanceRequired,
    LegalDocumentVersionOutdated,
    LegalError,
)
from wealthos.modules.organizations.domain.exceptions import OrganizationError
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

router = APIRouter()


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register user with first organization",
)
def register(
    payload: RegisterRequest,
    request: Request,
    command: Annotated[RegisterUserCommand, Depends(get_register_user_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> TokenResponse:
    try:
        with uow:
            result = command.execute(
                RegisterUserInput(
                    email=payload.email,
                    password=payload.password,
                    display_name=payload.display_name,
                    organization_name=payload.organization_name,
                    currency=payload.currency,
                    timezone=payload.timezone,
                    locale=payload.locale,
                    legal_acceptances=[
                        LegalAcceptanceItem(
                            document_type=item.document_type,
                            version=item.version,
                            accepted=item.accepted,
                            acknowledged=item.acknowledged,
                        )
                        for item in payload.legal_acceptances
                    ],
                    marketing_consent=payload.marketing_consent,
                    client_ip=_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                )
            )
            uow.commit()
    except UserEmailAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except LegalDocumentVersionOutdated as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc
    except LegalAcceptanceRequired as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc
    except LegalError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (InvalidEmail, DisplayNameEmpty, DisplayNameTooLong, WeakPassword) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except (IdentityError, OrganizationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return TokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    command: Annotated[LoginUserCommand, Depends(get_login_user_command)],
) -> TokenResponse:
    try:
        result = command.execute(
            LoginUserInput(email=form_data.username, password=form_data.password)
        )
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except InactiveUser as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    return TokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
    )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Current authenticated user",
)
def me(current_user: CurrentUser) -> CurrentUserResponse:
    return CurrentUserResponse.from_entity(current_user)
