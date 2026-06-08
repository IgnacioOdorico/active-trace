import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.api.v1.routers.audit import _resolve_audit_permission
from app.core.dependencies import get_current_user, get_db


class MockUser:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid.uuid4())
        self.tenant_id = kwargs.get("tenant_id", uuid.uuid4())
        self.email = kwargs.get("email", "test@test.com")
        self.is_active = True


def _make_mock_db(result_list=None, total=0):
    mock_db = AsyncMock(spec=["execute", "close"])
    mock_result = MagicMock()
    mock_result.unique.return_value.scalars.return_value.all.return_value = result_list or []
    mock_result.scalar_one.return_value = total
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.close = AsyncMock()
    return mock_db


class TestAuditLogEndpoint:
    @pytest.mark.asyncio
    async def test_endpoint_path(self):
        from app.api.v1.routers.audit import router
        routes = [r.path for r in router.routes]
        assert "/api/v1/admin/audit-log" in routes

    @pytest.mark.asyncio
    async def test_endpoint_requires_auth_without_override(self, async_client: AsyncClient):
        from app.main import app
        mock_db = _make_mock_db()
        app.dependency_overrides[get_db] = lambda: mock_db
        try:
            response = await async_client.get("/api/v1/admin/audit-log")
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_endpoint_returns_paginated_structure(self, async_client: AsyncClient):
        from app.main import app

        user = MockUser()
        mock_db = _make_mock_db()

        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[_resolve_audit_permission] = lambda: (True, None)

        try:
            response = await async_client.get(
                "/api/v1/admin/audit-log",
                headers={"Authorization": "Bearer test"},
            )
            assert response.status_code == 200
            body = response.json()
            assert "items" in body
            assert "total" in body
            assert "pagina" in body
            assert "por_pagina" in body
            assert "total_paginas" in body
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_endpoint_default_pagination_values(self, async_client: AsyncClient):
        from app.main import app

        user = MockUser()
        mock_db = _make_mock_db()

        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[_resolve_audit_permission] = lambda: (True, None)

        try:
            response = await async_client.get(
                "/api/v1/admin/audit-log",
                headers={"Authorization": "Bearer test"},
            )
            assert response.status_code == 200
            body = response.json()
            assert body["pagina"] == 1
            assert body["por_pagina"] == 50
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_forbidden_without_proper_token(self, async_client: AsyncClient):
        from app.main import app

        mock_db = _make_mock_db()
        app.dependency_overrides[get_db] = lambda: mock_db
        try:
            response = await async_client.get(
                "/api/v1/admin/audit-log",
                headers={"Authorization": "Bearer invalid-token"},
            )
            assert response.status_code in (401, 403)
        finally:
            app.dependency_overrides.clear()
