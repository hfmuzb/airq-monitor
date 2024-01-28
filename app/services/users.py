from typing import Annotated

from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.dependencies.auth_handler import oauth2_scheme
from api.dependencies.database import DbSessionDep
from schemas.auth_schemas import TokenData, User
from db.models import Users
from services.hash_password import verify_password
from core.config import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def authenticate_user(db_session: AsyncSession, username: str, password: str) -> Users | None | bool:
    user = await get_user(db_session, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


async def get_user(db_session: AsyncSession, username: str) -> Users | None:
    """
    Get user by username
    """
    user: Users = (
        await db_session.execute(
            select(Users).filter(Users.username == username)
        )
    ).scalar_one_or_none()
    return user


def create_access_token(data: dict) -> (str, str):
    """
    Creates access and refresh token JWTs and returns them
    """

    to_encode_access_token = data.copy()
    to_encode_refresh_token = data.copy()

    access_token_expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode_access_token.update({"exp": access_token_expire})
    to_encode_refresh_token.update({"exp": refresh_token_expire})

    encoded_access_jwt = jwt.encode(to_encode_access_token, SECRET_KEY, algorithm=ALGORITHM)
    encoded_refresh_jwt = jwt.encode(to_encode_refresh_token, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_access_jwt, encoded_refresh_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db_session=DbSessionDep,
) -> Users:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(db_session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def refresh_access_token(refresh_token: str | None = None) -> (str, str):
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token is not provided")
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        access_token, refresh_token = create_access_token(
            {"sub": username}
        )
        return access_token, refresh_token
    except JWTError:
        raise credentials_exception


def verify_token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """
    Verify token and return username; else raise credentials exception
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username
