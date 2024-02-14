from typing import Annotated

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from schemas.auth_schemas import User, RefreshToken
from services.users import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    refresh_access_token,
)
from api.dependencies.database import DbSessionDep

router = APIRouter()


@router.post("/auth/token", tags=["auth"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: DbSessionDep,
):
    user = await authenticate_user(db_session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token, refresh_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/auth/token/refresh", tags=["auth"])
async def post_refresh_access_token(
    token: RefreshToken,
):
    access_token, refresh_token = refresh_access_token(
        refresh_token=token.refresh_token
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/auth/users/me/", response_model=User, tags=["auth"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
