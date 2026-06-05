import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/activia_trace_test")
os.environ.setdefault("SECRET_KEY", "a" * 32)
os.environ.setdefault("ENCRYPTION_KEY", "b" * 32)

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.database import async_session_factory, close_db, init_db


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(
        _env_file=None,
        DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/activia_trace_test",
        SECRET_KEY="a" * 32,
        ENCRYPTION_KEY="b" * 32,
    )


@pytest_asyncio.fixture(scope="function")
async def db_session(settings: Settings) -> AsyncSession:
    init_db(settings.DATABASE_URL)
    async with async_session_factory() as session:  # type: ignore[union-attr]
        yield session
    await close_db()


@pytest_asyncio.fixture(scope="function")
async def async_client():
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
