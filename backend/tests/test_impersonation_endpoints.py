import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.core.dependencies import get_current_user, get_db


class MockUser:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid.uuid4())
        self.tenant_id = kwargs.get("tenant_id", uuid.uuid4())
        self.email = kwargs.get("email", "admin@test.com")
        self.is_active = True


def _make_mock_db():
    mock_db = AsyncMock(spec=["execute", "close"])
    mock_result = MagicMock()
    mock_result.unique.return_value.scalars.return_value.all.return_value = []
    mock_result.scalar_one.return_value = 0
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.close = AsyncMock()
    return mock_db


class TestImpersonationStartEndpoint:
    @pytest.mark.asyncio
    async def test_endpoint_path_exists(self):
        from app.api.v1.routers.audit import router
        paths = [r.path for r in router.routes]
        assert "/api/v1/admin/impersonation/start" in paths

    @pytest.mark.asyncio
    async def test_start_requires_auth(self, async_client: AsyncClient):
        from app.main import app
        mock_db = _make_mock_db()
        app.dependency_overrides[get_db] = lambda: mock_db
        try:
            response = await async_client.post("/api/v1/admin/impersonation/start", json={"target_user_id": str(uuid.uuid4())})
            assert response.status_code in (401, 403)
        finally:
            app.dependency_overrides.clear()


class TestImpersonationEndEndpoint:
    @pytest.mark.asyncio
    async def test_endpoint_path_exists(self):
        from app.api.v1.routers.audit import router
        paths = [r.path for r in router.routes]
        assert "/api/v1/admin/impersonation/end" in paths

    @pytest.mark.asyncio
    async def test_end_requires_auth(self, async_client: AsyncClient):
        from app.main import app
        mock_db = _make_mock_db()
        app.dependency_overrides[get_db] = lambda: mock_db
        try:
            response = await async_client.post("/api/v1/admin/impersonation/end")
            assert response.status_code in (401, 403)
        finally:
            app.dependency_overrides.clear()
