from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_user: str = "triage"
    postgres_password: str = "triage"
    postgres_db: str = "triage"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = "triage"

    mongo_user: str = "triage"
    mongo_password: str = "triage"
    mongo_db: str = "triage"
    mongo_host: str = "localhost"
    mongo_port: int = 27017

    openrouter_api_key: str = ""
    openrouter_model: str = "nvidia/nemotron-3.5-lightning:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    def postgres_dsn(self) -> str:
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql://{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    def redis_dsn(self) -> str:
        password = quote_plus(self.redis_password)
        return f"redis://:{password}@{self.redis_host}:{self.redis_port}/0"

    def mongo_dsn(self) -> str:
        user = quote_plus(self.mongo_user)
        password = quote_plus(self.mongo_password)
        return (
            f"mongodb://{user}:{password}"
            f"@{self.mongo_host}:{self.mongo_port}/{self.mongo_db}?authSource=admin"
        )


def load_settings(*, env_file: Path | None = _REPO_ROOT / ".env") -> Settings:
    # `_env_file` is a pydantic-settings init option, not a model field.
    if env_file is None:
        return Settings(_env_file=None)  # type: ignore[call-arg]
    return Settings(_env_file=env_file)  # type: ignore[call-arg]


def get_settings() -> Settings:
    return load_settings()
