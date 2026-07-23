"""HTTP routes for the identity module."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from wealthos.modules.identity.api.dependencies import (
    get_create_user_command,
    get_unit_of_work,
)
from wealthos.modules.identity.application.commands.create_user import (
    CreateUserCommand,
    CreateUserInput,
)
from wealthos.modules.identity.domain.exceptions import (
    DisplayNameEmpty,
    DisplayNameTooLong,
    IdentityError,
    InvalidEmail,
    UserEmailAlreadyExists,
)
from wealthos.modules.identity.schemas.create import UserCreate
from wealthos.modules.identity.schemas.response import UserResponse
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

router = APIRouter()


@router.get("/health", include_in_schema=False)
async def identity_module_health() -> dict[str, str]:
    return {"module": "identity", "status": "ready"}


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user (bootstrap / development)",
)
def create_user(
    payload: UserCreate,
    command: Annotated[CreateUserCommand, Depends(get_create_user_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> UserResponse:
    """Temporary public create-user endpoint until authentication lands."""
    try:
        with uow:
            user = command.execute(
                CreateUserInput(email=payload.email, display_name=payload.display_name)
            )
            uow.commit()
    except UserEmailAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (InvalidEmail, DisplayNameEmpty, DisplayNameTooLong) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except IdentityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UserResponse.from_entity(user)
