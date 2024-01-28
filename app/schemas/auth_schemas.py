from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_toke: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class RefreshToken(BaseModel):
    refresh_token: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
