"""Application configuration from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = Field(default="Event Discovery Service", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    environment: Literal["development", "testing", "production"] = Field(
        default="development", description="Environment"
    )

    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 URL prefix")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/eventdb",
        description="PostgreSQL connection URL (async)",
    )
    database_url_sync: str | None = Field(
        default=None,
        description="Synchronous URL for Alembic; derived from database_url if not set",
    )

    # Security
    secret_key: str = Field(
        default="change-me-in-production-use-env-secret-key",
        description="Secret key for JWT; must be set via env in production",
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=60 * 24, description="Access token TTL in minutes")

    # CORS
    cors_origins: list[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000"])

    # Pagination
    default_page_size: int = Field(default=20, ge=1, le=100)
    max_page_size: int = Field(default=100, ge=1, le=500)

    def get_database_url_sync(self) -> str:
        """Return sync URL for Alembic (replace asyncpg with psycopg2)."""
        if self.database_url_sync:
            return self.database_url_sync
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
