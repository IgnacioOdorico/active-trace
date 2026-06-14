import uuid
from datetime import datetime, timedelta, timezone
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
        "rols": ["COORDINADOR"],
    }


@pytest.fixture
def auth_header(mock_auth_user):
    with patch("app.core.auth.decode_access_token", return_value=mock_auth_user):
        yield {"Authorization": "Bearer fake-token"}


@pytest.fixture
def async_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


def _make_mock_asignacion(asignacion_id=None):
    aid = asignacion_id or uuid.uuid4()
    now = datetime.now(timezone.utc)
    a = Mock()
    a.id = aid
    a.tenant_id = uuid.uuid4()
    a.usuario_id = str(uuid.uuid4())
    a.rol = "PROFESOR"
    a.materia_id = str(uuid.uuid4())
    a.carrera_id = None
    a.cohorte_id = str(uuid.uuid4())
    a.comisiones = ["A", "B"]
    a.responsable_id = None
    a.desde = now - timedelta(days=30)
    a.hasta = now + timedelta(days=30)
    a.estado_vigencia = "Vigente"
    a.created_at = now
    a.updated_at = now
    return a


class TestAsignacionesEndpoints:
    @pytest.mark.asyncio
    async def test_create_asignacion_returns_201(self, async_client, auth_header):
        with patch("app.services.asignacion_service.AsignacionRepository") as mock_repo:
            mock_repo.return_value.create = AsyncMock(
                return_value=_make_mock_asignacion()
            )

            response = await async_client.post(
                "/api/asignaciones",
                json={
                    "usuario_id": str(uuid.uuid4()),
                    "rol": "PROFESOR",
                    "materia_id": str(uuid.uuid4()),
                    "cohorte_id": str(uuid.uuid4()),
                    "comisiones": ["A"],
                    "desde": (
                        datetime.now(timezone.utc) - timedelta(days=30)
                    ).isoformat(),
                },
                headers=auth_header,
            )
            assert response.status_code == 201
            data = response.json()
            assert data["rol"] == "PROFESOR"
            assert data["estado_vigencia"] == "Vigente"

    @pytest.mark.asyncio
    async def test_create_asignacion_no_auth_returns_401(self, async_client):
        response = await async_client.post(
            "/api/asignaciones",
            json={
                "usuario_id": str(uuid.uuid4()),
                "rol": "PROFESOR",
                "desde": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_asignaciones_returns_200(self, async_client, auth_header):
        with patch("app.services.asignacion_service.AsignacionRepository") as mock_repo:
            mock_repo.return_value.get_all = AsyncMock(return_value=[])
            mock_repo.return_value.count = AsyncMock(return_value=0)

            response = await async_client.get("/api/asignaciones", headers=auth_header)
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "total" in data

    @pytest.mark.asyncio
    async def test_update_asignacion_returns_200(self, async_client, auth_header):
        asignacion_id = uuid.uuid4()
        mock_a = _make_mock_asignacion(asignacion_id=asignacion_id)

        with patch("app.services.asignacion_service.AsignacionRepository") as mock_repo:
            mock_repo.return_value.get = AsyncMock(return_value=mock_a)
            mock_repo.return_value.update = AsyncMock(return_value=mock_a)

            response = await async_client.patch(
                f"/api/asignaciones/{asignacion_id}",
                json={"rol": "TUTOR"},
                headers=auth_header,
            )
            assert response.status_code == 200
            assert response.json()["rol"] == "PROFESOR"

    @pytest.mark.asyncio
    async def test_update_asignacion_not_found_returns_404(
        self, async_client, auth_header
    ):
        with patch("app.services.asignacion_service.AsignacionRepository") as mock_repo:
            mock_repo.return_value.get = AsyncMock(return_value=None)

            response = await async_client.patch(
                f"/api/asignaciones/{uuid.uuid4()}",
                json={"rol": "TUTOR"},
                headers=auth_header,
            )
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_asignacion_returns_204(self, async_client, auth_header):
        mock_a = _make_mock_asignacion()
        with patch("app.services.asignacion_service.AsignacionRepository") as mock_repo:
            mock_repo.return_value.get = AsyncMock(return_value=mock_a)
            mock_repo.return_value.soft_delete = AsyncMock()

            response = await async_client.delete(
                f"/api/asignaciones/{uuid.uuid4()}", headers=auth_header
            )
            assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_asignaciones_403_without_permission(self, async_client):
        mock_auth = {
            "sub": str(uuid.uuid4()),
            "tenant_id": str(uuid.uuid4()),
            "rols": [],
        }
        with patch("app.core.auth.decode_access_token", return_value=mock_auth):
            response = await async_client.post(
                "/api/asignaciones",
                json={
                    "usuario_id": str(uuid.uuid4()),
                    "rol": "PROFESOR",
                    "desde": datetime.now(timezone.utc).isoformat(),
                },
                headers={"Authorization": "Bearer no-perms"},
            )
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_asignaciones_filters_by_usuario(
        self, async_client, auth_header
    ):
        usuario_id = str(uuid.uuid4())
        with patch("app.services.asignacion_service.AsignacionRepository") as mock_repo:
            mock_repo.return_value.get_all = AsyncMock(return_value=[])
            mock_repo.return_value.count = AsyncMock(return_value=0)

            response = await async_client.get(
                f"/api/asignaciones?usuario_id={usuario_id}",
                headers=auth_header,
            )
            assert response.status_code == 200
