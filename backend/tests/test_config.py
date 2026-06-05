import pytest
from pydantic import ValidationError


class TestSettings:
    def test_valid_instantiation(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

        from app.core.config import Settings

        settings = Settings(_env_file=None)
        assert str(settings.DATABASE_URL) == "postgresql+asyncpg://user:pass@localhost:5432/db"
        assert settings.SECRET_KEY == "a" * 32
        assert settings.ENCRYPTION_KEY == "b" * 32
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_default_access_token_expire(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)

        from app.core.config import Settings

        settings = Settings(_env_file=None)
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 15

    def test_missing_database_url_fails(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)

        from app.core.config import Settings

        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_short_secret_key_fails(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
        monkeypatch.setenv("SECRET_KEY", "short")
        monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)

        from app.core.config import Settings

        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_wrong_encryption_key_length_fails(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("ENCRYPTION_KEY", "short")

        from app.core.config import Settings

        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_missing_secret_key_fails(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.setenv("ENCRYPTION_KEY", "a" * 32)

        from app.core.config import Settings

        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_invalid_token_expire_type_fails(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "not-a-number")

        from app.core.config import Settings

        with pytest.raises(ValidationError):
            Settings(_env_file=None)
