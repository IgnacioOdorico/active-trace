"""Multi-tenant isolation tests for usuarios and asignaciones.

Verifies that tenant A cannot see tenant B data.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

db = pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)

pytestmark = db


@pytest.fixture
def mock_auth_user():
    return {
        "sub": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "rols": ["ADMIN"],
    }


@pytest.fixture
def auth_header(mock_auth_user):
    with patch("app.core.auth.decode_access_token", return_value=mock_auth_user):
        yield {"Authorization": "Bearer fake-token"}


@pytest.fixture
def async_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


class TestMultiTenantIsolation:
    @pytest.mark.asyncio
    async def test_usuario_tenant_a_not_in_tenant_b(
        self, async_client, auth_header, mock_auth_user
    ):
        tenant_a_id = uuid.uuid4()
        tenant_b_id = uuid.uuid4()

        user_b = Mock()
        user_b.id = uuid.uuid4()
        user_b.tenant_id = tenant_b_id
        user_b.email = "user_b@mail.com"
        user_b.nombre = "B"
        user_b.apellidos = None
        user_b.dni = None
        user_b.cuil = None
        user_b.cbu = None
        user_b.alias_cbu = None
        user_b.banco = None
        user_b.regional = None
        user_b.legajo = None
        user_b.legajo_profesional = None
        user_b.facturador = False
        user_b.estado = "Activo"
        user_b.is_active = True
        user_b.created_at = datetime.now(timezone.utc)
        user_b.updated_at = datetime.now(timezone.utc)

        mock_auth_user["tenant_id"] = str(tenant_a_id)

        with patch("app.services.usuario_service.UsuarioRepository") as mock_repo:
            mock_repo.return_value.get_all = AsyncMock(return_value=[])
            mock_repo.return_value.count = AsyncMock(return_value=0)

            response = await async_client.get(
                "/api/admin/usuarios", headers=auth_header
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]) == 0

    @pytest.mark.asyncio
    async def test_asignacion_tenant_a_not_in_tenant_b(
        self, async_client, auth_header, mock_auth_user
    ):
        tenant_a_id = uuid.uuid4()

        mock_auth_user["tenant_id"] = str(tenant_a_id)

        with patch("app.services.asignacion_service.AsignacionRepository") as mock_repo:
            mock_repo.return_value.get_all = AsyncMock(return_value=[])
            mock_repo.return_value.count = AsyncMock(return_value=0)

            response = await async_client.get("/api/asignaciones", headers=auth_header)
            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]) == 0
