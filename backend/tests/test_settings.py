import pytest

from triage_copilot.settings import load_settings

_ENV_KEYS = (
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "REDIS_HOST",
    "REDIS_PORT",
    "REDIS_PASSWORD",
    "MONGO_USER",
    "MONGO_PASSWORD",
    "MONGO_DB",
    "MONGO_HOST",
    "MONGO_PORT",
    "OPENROUTER_API_KEY",
    "OPENROUTER_MODEL",
    "OPENROUTER_BASE_URL",
)


def test_defaults_match_compose(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    settings = load_settings(env_file=None)

    assert settings.postgres_dsn() == "postgresql://triage:triage@localhost:5432/triage"
    assert settings.redis_dsn() == "redis://:triage@localhost:6379/0"
    assert (
        settings.mongo_dsn()
        == "mongodb://triage:triage@localhost:27017/triage?authSource=admin"
    )
    assert settings.openrouter_api_key == ""
    assert settings.openrouter_model == "nvidia/nemotron-3.5-lightning:free"


def test_environment_overrides_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("POSTGRES_USER", "from-env")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.setenv("REDIS_PASSWORD", "p@ss")

    settings = load_settings(env_file=None)

    assert settings.postgres_user == "from-env"
    assert settings.postgres_port == 5433
    assert settings.redis_dsn() == "redis://:p%40ss@localhost:6379/0"
