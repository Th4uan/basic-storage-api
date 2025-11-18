import os
from functools import lru_cache
from typing import List

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "document-storage-api"
    secret_key: str = Field(..., validation_alias=AliasChoices("APP_SECRET_KEY", "SECRET_KEY"))
    access_token_exp_minutes: int = Field(
        15,
        validation_alias=AliasChoices("ACCESS_TOKEN_EXP_MINUTES", "ACCESS_TOKEN_EXPIRE_MINUTES"),
    )
    refresh_token_exp_minutes: int = Field(
        60 * 24 * 7,
        validation_alias=AliasChoices("REFRESH_TOKEN_EXP_MINUTES", "REFRESH_TOKEN_EXPIRE_MINUTES"),
    )
    jwt_algorithm: str = Field("HS256", validation_alias=AliasChoices("JWT_ALGORITHM", "ALGORITHM"))
    database_url: str = Field(..., validation_alias=AliasChoices("DATABASE_URL", "DB_URL"))
    cors_allow_origins: List[str] = Field(
        default_factory=lambda: ["*"],
        validation_alias=AliasChoices("CORS_ALLOW_ORIGINS", "CORS_ALLOWED_ORIGINS"),
    )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("APP_SECRET_KEY must be at least 32 characters long")
        return value

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if value is None:
            return ["*"]
        if isinstance(value, str):
            items = [origin.strip() for origin in value.split(",") if origin.strip()]
            return items or ["*"]
        if isinstance(value, (list, tuple)):
            return list(value)
        raise ValueError("Invalid format for CORS_ALLOW_ORIGINS")


@lru_cache
def get_settings() -> Settings:
    if "DATABASE_URL" not in os.environ:
        os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:postgres@db:5432/app_db"
    return Settings()
