import warnings
from typing import Literal

from pydantic import BaseSettings, Field, validator

DEFAULT_AES = "CYwwvJYRRsrPHhwV5qkuRdXLOw9jwsii2A9pEaKI6T0="


class Settings(BaseSettings):
    name: str = "Konfigure"
    log_level: Literal["debug", "info", "warning", "error", "critical"] = Field(
        "info", env="LOG_LEVEL"
    )
    AES_KEY: str = Field("CYwwvJYRRsrPHhwV5qkuRdXLOw9jwsii2A9pEaKI6T0=", env="AES_KEY")
    DB_URL: str = Field(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/configuration",
        env="DB_URL",
    )
    POOL_SIZE: int = Field(10, env="CONNECTION_POOL_SIZE")

    @validator("AES_KEY")
    def ensure_aes_not_default(cls, v: str):
        if v == DEFAULT_AES:
            warnings.warn("Using default AES KEY, should not be used in production")
        return v


settings = Settings()
