"""
Application configuration management.
"""

import logging
import secrets
from functools import lru_cache
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Insecure default that must be changed in production
_INSECURE_DEFAULT_KEY = "your-secret-key-change-in-production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Application
    APP_NAME: str = "Leave Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/lms_db"
    SQL_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Security
    SECRET_KEY: str = _INSECURE_DEFAULT_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # SSO/OAuth2
    OAUTH2_ENABLED: bool = False
    OAUTH2_PROVIDER_URL: Optional[str] = None
    OAUTH2_CLIENT_ID: Optional[str] = None
    OAUTH2_CLIENT_SECRET: Optional[str] = None

    # CORS
    # Comma-separated list of allowed origins. If empty, allow_origin_regex is used.
    CORS_ALLOW_ORIGINS: str = ""
    # Default to allowing localhost/127.0.0.1 during local development.
    CORS_ALLOW_ORIGIN_REGEX: str = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
    CORS_ALLOW_CREDENTIALS: bool = False

    # Audit
    AUDIT_RETENTION_DAYS: int = 365 * 7  # 7 years default

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        """Ensure SECRET_KEY is secure in production.

        CRITICAL: Using default SECRET_KEY in production is a security vulnerability.
        Attackers could forge JWT tokens and impersonate any user.
        """
        if self.SECRET_KEY == _INSECURE_DEFAULT_KEY:
            if not self.DEBUG:
                # In production, fail loudly
                raise ValueError(
                    "CRITICAL SECURITY ERROR: SECRET_KEY must be set to a secure random value "
                    'in production. Generate one with: python -c "import secrets; print(secrets.token_urlsafe(32))"'
                )
            else:
                # In debug mode, warn but allow (for local development convenience)
                logging.warning(
                    "⚠️  WARNING: Using insecure default SECRET_KEY. "
                    "This is acceptable for local development only. "
                    "Set SECRET_KEY environment variable for any shared/deployed environment."
                )
        return self


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
