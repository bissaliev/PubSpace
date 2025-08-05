from pathlib import Path
from typing import Any

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    BASE_DIR: Path = Path(__file__).parent.parent
    SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECOND: int
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    VERIFICATION_TOKEN_LIFETIME_SECONDS: int = 3600  # 1 час
    FRONTEND_URL: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    DATABASE_URL: PostgresDsn | str = ""

    @field_validator("DATABASE_URL", mode="after")
    def assemble_async_db_connection(
        cls, v: str | None, info: FieldValidationInfo
    ) -> Any:
        if isinstance(v, str) and v == "":
            return PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=info.data["POSTGRES_USER"],
                password=info.data["POSTGRES_PASSWORD"],
                host=info.data["POSTGRES_HOST"],
                port=info.data["POSTGRES_PORT"],
                path=info.data["POSTGRES_DB"],
            )
        return v

    BACKEND_CORS_ORIGINS: str | list[AnyHttpUrl] = "http://localhost"

    @field_validator("BACKEND_CORS_ORIGINS", mode="after")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


settings = Setting()
