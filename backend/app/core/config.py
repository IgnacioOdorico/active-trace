from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    DATABASE_URL: str = Field(...)
    SECRET_KEY: str = Field(..., min_length=32)
    ENCRYPTION_KEY: str = Field(...)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, ge=1)
    DATABASE_URL_TEST: str | None = Field(default=None)
    OTEL_SERVICE_NAME: str = Field(default="activia-trace")
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = Field(default=None)
    OTEL_ENABLED: bool = Field(default=False)
    FACTURAS_DIR: str = Field(default="/data/facturas")
    MAX_FILE_SIZE_KB: int = Field(default=10240)

    @model_validator(mode="after")
    def validate_encryption_key_length(self):
        if len(self.ENCRYPTION_KEY) != 32:
            raise ValueError(
                f"ENCRYPTION_KEY must be exactly 32 characters, got {len(self.ENCRYPTION_KEY)}"
            )
        return self


settings = Settings()  # type: ignore[call-arg]
