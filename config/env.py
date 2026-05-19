from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=BASE_DIR / ".env", extra="ignore")

    host: str = "localhost"
    port: int = 5432
    name: str = "cassa"
    user: str = "cassa"
    password: str = "cassa"

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", env_file=BASE_DIR / ".env", extra="ignore")

    url: str = "redis://localhost:6379/0"


class StripeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="STRIPE_", env_file=BASE_DIR / ".env", extra="ignore"
    )

    secret_key: str = ""
    publishable_key: str = ""
    webhook_secret: str = ""


class StorageSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AWS_", env_file=BASE_DIR / ".env", extra="ignore"
    )

    access_key_id: str = ""
    secret_access_key: str = ""
    storage_bucket_name: str = "cassa-media"
    s3_endpoint_url: str = ""
    s3_custom_domain: str = ""
    default_region: str = "us-east-1"


class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EMAIL_", env_file=BASE_DIR / ".env", extra="ignore"
    )

    backend: str = "django.core.mail.backends.smtp.EmailBackend"
    host: str = "localhost"
    port: int = 1025
    use_tls: bool = False
    host_user: str = ""
    host_password: str = ""
    default_from: str = "noreply@cassa.io"


class SentrySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SENTRY_", env_file=BASE_DIR / ".env", extra="ignore"
    )

    dsn: str = ""
    environment: str = "development"
    traces_sample_rate: float = 0.1


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    django_env: Literal["development", "production", "testing"] = "development"
    secret_key: str = "insecure-dev-secret-change-in-production"
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    cors_allowed_origins: list[str] = []

    currency: str = "USD"
    store_name: str = "Cassa"
    store_url: str = "http://localhost:8000"

    google_client_id: str = ""
    google_client_secret: str = ""

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_hosts(cls, v: object) -> object:
        if isinstance(v, str):
            return [h.strip() for h in v.split(",") if h.strip()]
        return v

    @property
    def debug(self) -> bool:
        return self.django_env == "development"

    @property
    def testing(self) -> bool:
        return self.django_env == "testing"


# Instantiate once; import from here everywhere
settings = Settings()
db = DatabaseSettings()
redis = RedisSettings()
stripe = StripeSettings()
storage = StorageSettings()
email = EmailSettings()
sentry = SentrySettings()
