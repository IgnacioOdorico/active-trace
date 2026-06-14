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


def _make_mock_user(user_id=None, tenant_id=None, email="test@mail.com"):
    uid = user_id or uuid.uuid4()
    tid = tenant_id or uuid.uuid4()
    mock_user = Mock()
    mock_user.id = uid
    mock_user.tenant_id = tid
    mock_user.nombre = "Juan"
    mock_user.apellidos = "Pérez"
    mock_user.email = email
    mock_user.dni = "12345678"
    mock_user.cuil = "20-12345678-9"
    mock_user.cbu = "0000003100000000000001"
    mock_user.alias_cbu = None
    mock_user.banco = "Nación"
    mock_user.regional = "CABA"
    mock_user.legajo = "LEG-001"
    mock_user.legajo_profesional = None
    mock_user.facturador = False
    mock_user.estado = "Activo"
    mock_user.is_active = True
    mock_user.created_at = datetime.now(timezone.utc)
    mock_user.updated_at = datetime.now(timezone.utc)
    return mock_user


class TestUsuariosEndpoints:
    @pytest.mark.asyncio
    async def test_create_usuario_returns_201(self, async_client, auth_header):
        with patch("app.services.usuario_service.UsuarioRepository") as mock_repo:
            mock_repo.return_value.get_by_email = AsyncMock(return_value=None)
            mock_repo.return_value.create = AsyncMock(return_value=_make_mock_user())
            response = await async_client.post(
                "/api/admin/usuarios",
                json={
                    "nombre": "Juan",
                    "apellidos": "Pérez",
                    "email": "juan@mail.com",
                    "dni": "12345678",
                },
                headers=auth_header,
            )
            assert response.status_code == 201
            data = response.json()
            assert data["nombre"] == "Juan"
            assert data["email"] == "juan@mail.com"

    @pytest.mark.asyncio
    async def test_create_usuario_duplicate_email_returns_409(
        self, async_client, auth_header
    ):
        with patch("app.services.usuario_service.UsuarioRepository") as mock_repo:
            mock_repo.return_value.get_by_email = AsyncMock(
                return_value=_make_mock_user()
            )
            response = await async_client.post(
                "/api/admin/usuarios",
                json={
                    "nombre": "Juan",
                    "email": "dup@mail.com",
                },
                headers=auth_header,
            )
            assert response.status_code == 409
            assert response.json()["detail"] == "EMAIL_DUPLICADO"

    @pytest.mark.asyncio
    async def test_create_usuario_no_auth_returns_401(self, async_client):
        response = await async_client.post(
            "/api/admin/usuarios",
            json={"email": "test@mail.com"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_usuarios_returns_200(self, async_client, auth_header):
        with patch("app.services.usuario_service.UsuarioRepository") as mock_repo:
            mock_repo.return_value.get_all = AsyncMock(return_value=[])
            mock_repo.return_value.count = AsyncMock(return_value=0)

            response = await async_client.get(
                "/api/admin/usuarios", headers=auth_header
            )
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "total" in data

    @pytest.mark.asyncio
    async def test_update_usuario_returns_200(self, async_client, auth_header):
        user_id = uuid.uuid4()
        mock_user = _make_mock_user(user_id=user_id)

        with patch("app.services.usuario_service.UsuarioRepository") as mock_repo:
            mock_repo.return_value.get = AsyncMock(return_value=mock_user)
            mock_repo.return_value.update = AsyncMock(return_value=mock_user)

            response = await async_client.patch(
                f"/api/admin/usuarios/{user_id}",
                json={"nombre": "Updated"},
                headers=auth_header,
            )
            assert response.status_code == 200
            assert response.json()["nombre"] == "Juan"

    @pytest.mark.asyncio
    async def test_update_usuario_not_found_returns_404(
        self, async_client, auth_header
    ):
        with patch("app.services.usuario_service.UsuarioRepository") as mock_repo:
            mock_repo.return_value.get = AsyncMock(return_value=None)

            response = await async_client.patch(
                f"/api/admin/usuarios/{uuid.uuid4()}",
                json={"nombre": "Nope"},
                headers=auth_header,
            )
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_usuario_returns_204(self, async_client, auth_header):
        with patch("app.services.usuario_service.UsuarioRepository") as mock_repo:
            mock_user = _make_mock_user()
            mock_repo.return_value.get = AsyncMock(return_value=mock_user)
            mock_repo.return_value.soft_delete = AsyncMock()

            response = await async_client.delete(
                f"/api/admin/usuarios/{uuid.uuid4()}", headers=auth_header
            )
            assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_usuarios_403_without_permission(self, async_client):
        mock_auth = {
            "sub": str(uuid.uuid4()),
            "tenant_id": str(uuid.uuid4()),
            "rols": [],
        }
        with patch("app.core.auth.decode_access_token", return_value=mock_auth):
            response = await async_client.post(
                "/api/admin/usuarios",
                json={"email": "test@mail.com"},
                headers={"Authorization": "Bearer no-perms"},
            )
            assert response.status_code == 403
