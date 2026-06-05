import pytest
from httpx import AsyncClient

from app.core.dependencies import get_db


class MockResult:
    def scalar_one(self):
        return 1


class MockSession:
    async def execute(self, *args, **kwargs):
        return MockResult()

    async def close(self):
        pass


class FailingSession:
    async def execute(self, *args, **kwargs):
        msg = "DB is down"
        raise ConnectionError(msg)

    async def close(self):
        pass


async def override_get_db_success():
    yield MockSession()


async def override_get_db_failure():
    yield FailingSession()


@pytest.mark.asyncio
async def test_health_returns_200(async_client: AsyncClient):
    from app.main import app

    app.dependency_overrides[get_db] = override_get_db_success
    try:
        response = await async_client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["database"] == "up"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_db_down(async_client: AsyncClient):
    from app.main import app

    app.dependency_overrides[get_db] = override_get_db_failure
    try:
        response = await async_client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["database"] == "down"
        assert body["status"] == "ok"
    finally:
        app.dependency_overrides.clear()
