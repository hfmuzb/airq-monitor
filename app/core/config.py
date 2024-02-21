import os
from enum import Enum
from functools import lru_cache
from typing import Optional, Set

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentEnum(str, Enum):
    PRODUCTION = "production"
    DEVELOP = "develop"


class GlobalSettings(BaseSettings):
    PROJECT_NAME: str = "Air quality monitoring, Uzbekistan"
    API_V1_STR: str = "/v1"

    DOCS_USERNAME: str = "docs_user"
    DOCS_PASSWORD: str = "simple_password"

    API_DOMAIN: str = "127.0.0.1"
    TRUSTED_HOSTS: Set[str] = {"localhost", "127.0.0.1", "0.0.0.0"}
    BACKEND_CORS_ORIGINS: Set[HttpUrl] = set()
    ALLOWED_CORS_HEADERS: Set[str] = {"*"}
    ALLOWED_CORS_METHODS: Set[str] = {
        "GET",
        "PUT",
        "POST",
        "DELETE",
        "OPTIONS",
        "PATCH",
    }

    ENVIRONMENT: EnvironmentEnum
    DEBUG: bool = False

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 300
    SECRET_KEY: str = "super_secret_key"
    ALGORITHM: str = "HS256"

    DEVICE_DATA_SECRET_KEY: str = "super_secret_key"
    DEVICE_DATA_ALGORITHM: str = "HS256"

    DATABASE_URL: Optional[str] = "postgresql://user:pass@localhost:6432/my_db"
    DB_ECHO_LOG: bool = False

    @property
    def async_database_url(self) -> Optional[str]:
        return (
            str(self.DATABASE_URL)
            .replace("postgresql://", "postgresql+asyncpg://")
            .replace("sslmode=", "ssl=")
            if self.DATABASE_URL
            else str(self.DATABASE_URL)
        )

    model_config = SettingsConfigDict(case_sensitive=True)


class DevelopSettings(GlobalSettings):
    DEBUG: bool = True
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.DEVELOP


class ProductionSettings(GlobalSettings):
    DEBUG: bool = False
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.PRODUCTION


class FactoryConfig:
    def __init__(self, environment: Optional[str]):
        self.environment = environment

    def __call__(self) -> GlobalSettings:
        match self.environment:
            case EnvironmentEnum.PRODUCTION:
                return ProductionSettings()
            case _:
                return DevelopSettings()


@lru_cache()
def get_configuration() -> GlobalSettings:
    return FactoryConfig(os.environ.get("ENVIRONMENT"))()


settings = get_configuration()
