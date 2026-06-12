from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings.

    All sensitive data is loaded from environment
    variables or the .env file.

    Used by:
    - PostgreSQL / SQLite
    - JWT authentication
    - Redis cache
    - Email service
    """

    # Database

    database_url: str = Field(
        ...,
        alias="DATABASE_URL",
        description="Database connection URL",
    )

    # JWT

    secret_key: str = Field(
        ...,
        alias="SECRET_KEY",
        description="JWT secret key",
    )

    algorithm: str = Field(
        default="HS256",
        alias="ALGORITHM",
        description="JWT signing algorithm",
    )

    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
        description="Access token lifetime in minutes",
    )

    refresh_token_expire_days: int = Field(
        default=7,
        alias="REFRESH_TOKEN_EXPIRE_DAYS",
        description="Refresh token lifetime in days",
    )

    # Redis

    redis_host: str = Field(
        default="localhost",
        alias="REDIS_HOST",
        description="Redis host",
    )

    redis_port: int = Field(
        default=6379,
        alias="REDIS_PORT",
        description="Redis port",
    )

    # Email

    mail_username: str = Field(
        ...,
        alias="MAIL_USERNAME",
    )

    mail_password: str = Field(
        ...,
        alias="MAIL_PASSWORD",
    )

    mail_from: str = Field(
        ...,
        alias="MAIL_FROM",
    )

    mail_port: int = Field(
        default=587,
        alias="MAIL_PORT",
    )

    mail_server: str = Field(
        ...,
        alias="MAIL_SERVER",
    )

    mail_starttls: bool = Field(
        default=True,
        alias="MAIL_STARTTLS",
    )

    mail_ssl_tls: bool = Field(
        default=False,
        alias="MAIL_SSL_TLS",
    )

    # Cloudinary (якщо використовується для аватарів)

    cloudinary_name: str | None = Field(
        default=None,
        alias="CLOUDINARY_NAME",
    )

    cloudinary_api_key: str | None = Field(
        default=None,
        alias="CLOUDINARY_API_KEY",
    )

    cloudinary_api_secret: str | None = Field(
        default=None,
        alias="CLOUDINARY_API_SECRET",
    )

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm