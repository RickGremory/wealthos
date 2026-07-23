from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central runtime configuration for the WealthOS API."""

    app_name: str = "WealthOS API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    database_url: str = Field(
        default="postgresql+psycopg://wealthos:wealthos@localhost:5433/wealthos",
        description="SQLAlchemy URL (sync driver for Pack 3).",
    )
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_recycle: int = 1800
    db_echo: bool = False

    redis_url: str = "redis://localhost:6379/0"

    # Auth / JWT
    auth_jwt_secret: str = Field(
        default="dev-only-change-me-to-a-long-random-secret",
        description="HMAC secret for access tokens.",
    )
    auth_jwt_algorithm: str = "HS256"
    auth_access_token_expire_minutes: int = 15
    auth_jwt_issuer: str = "wealthos-api"
    auth_jwt_audience: str = "wealthos-web"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_development(self) -> bool:
        return self.environment.lower() in {"development", "dev", "local"}

    @property
    def sqlalchemy_echo(self) -> bool:
        return self.db_echo or (self.debug and self.is_development)


@lru_cache
def get_settings() -> Settings:
    return Settings()
