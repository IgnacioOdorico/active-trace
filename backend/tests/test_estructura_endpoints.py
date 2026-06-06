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
    return {"sub": str(uuid.uuid4()), "tenant_id": str(uuid.uuid4()), "rols": ["ADMIN"]}


@pytest.fixture
def auth_header(mock_auth_user):
    with patch("app.core.auth.decode_access_token", return_value=mock_auth_user):
        yield {"Authorization": "Bearer fake-token"}


@pytest.fixture
def async_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_carrera_create_returns_201(async_client, auth_header):
    with patch("app.services.carrera_service.BaseRepository") as mock_repo:
        mock_instance = Mock()
        mock_instance.id = uuid.uuid4()
        mock_instance.codigo = "ING"
        mock_instance.nombre = "Ingeniería"
        mock_instance.descripcion = None
        mock_instance.activa = True
        mock_instance.created_at = datetime.now(timezone.utc)
        mock_instance.updated_at = datetime.now(timezone.utc)

        mock_repo.return_value.create = AsyncMock(return_value=mock_instance)
        mock_repo.return_value.get_all = AsyncMock(return_value=[])

        response = await async_client.post(
            "/api/v1/admin/carreras",
            json={"codigo": "ING", "nombre": "Ingeniería"},
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["codigo"] == "ING"
        assert data["nombre"] == "Ingeniería"


@pytest.mark.asyncio
async def test_carrera_list_returns_200(async_client, auth_header):
    with patch("app.services.carrera_service.BaseRepository") as mock_repo:
        mock_repo.return_value.get_all = AsyncMock(return_value=[])

        response = await async_client.get(
            "/api/v1/admin/carreras", headers=auth_header
        )
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
async def test_carrera_get_returns_200(async_client, auth_header):
    carrera_id = uuid.uuid4()
    mock_instance = Mock()
    mock_instance.id = carrera_id
    mock_instance.codigo = "ING"
    mock_instance.nombre = "Ingeniería"
    mock_instance.descripcion = None
    mock_instance.activa = True
    mock_instance.created_at = datetime.now(timezone.utc)
    mock_instance.updated_at = datetime.now(timezone.utc)

    with patch("app.services.carrera_service.BaseRepository") as mock_repo:
        mock_repo.return_value.get = AsyncMock(return_value=mock_instance)

        response = await async_client.get(
            f"/api/v1/admin/carreras/{carrera_id}", headers=auth_header
        )
        assert response.status_code == 200
        assert response.json()["codigo"] == "ING"


@pytest.mark.asyncio
async def test_carrera_get_not_found_returns_404(async_client, auth_header):
    with patch("app.services.carrera_service.BaseRepository") as mock_repo:
        mock_repo.return_value.get = AsyncMock(return_value=None)

        response = await async_client.get(
            f"/api/v1/admin/carreras/{uuid.uuid4()}", headers=auth_header
        )
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_carrera_update_returns_200(async_client, auth_header):
    carrera_id = uuid.uuid4()
    mock_instance = Mock()
    mock_instance.id = carrera_id
    mock_instance.codigo = "ING"
    mock_instance.nombre = "Updated"
    mock_instance.descripcion = None
    mock_instance.activa = True
    mock_instance.created_at = datetime.now(timezone.utc)
    mock_instance.updated_at = datetime.now(timezone.utc)

    with patch("app.services.carrera_service.BaseRepository") as mock_repo:
        mock_repo.return_value.get = AsyncMock(return_value=mock_instance)
        mock_repo.return_value.update = AsyncMock(return_value=mock_instance)

        response = await async_client.put(
            f"/api/v1/admin/carreras/{carrera_id}",
            json={"nombre": "Updated"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Updated"


@pytest.mark.asyncio
async def test_carrera_delete_returns_204(async_client, auth_header):
    with patch("app.services.carrera_service.BaseRepository") as mock_repo:
        mock_repo.return_value.soft_delete = AsyncMock()

        response = await async_client.delete(
            f"/api/v1/admin/carreras/{uuid.uuid4()}", headers=auth_header
        )
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_cohorte_create_returns_201(async_client, auth_header):
    carrera_id = uuid.uuid4()

    with patch("app.services.cohorte_service.BaseRepository") as mock_repo:
        with patch("app.services.carrera_service.BaseRepository") as mock_carrera_repo:
            mock_carrera = Mock()
            mock_carrera.activa = True
            mock_carrera_repo.return_value.get = AsyncMock(return_value=mock_carrera)

            mock_instance = Mock()
            mock_instance.id = uuid.uuid4()
            mock_instance.nombre = "2026A"
            mock_instance.carrera_id = carrera_id
            mock_instance.fecha_inicio = datetime.now(timezone.utc)
            mock_instance.fecha_fin = datetime.now(timezone.utc)
            mock_instance.activa = True
            mock_instance.created_at = datetime.now(timezone.utc)
            mock_instance.updated_at = datetime.now(timezone.utc)
            mock_repo.return_value.create = AsyncMock(return_value=mock_instance)

            response = await async_client.post(
                "/api/v1/admin/cohortes",
                json={
                    "nombre": "2026A",
                    "carrera_id": str(carrera_id),
                    "fecha_inicio": "2026-01-01T00:00:00Z",
                    "fecha_fin": "2026-12-31T00:00:00Z",
                },
                headers=auth_header,
            )
            assert response.status_code == 201
            assert response.json()["nombre"] == "2026A"


@pytest.mark.asyncio
async def test_cohorte_list_returns_200(async_client, auth_header):
    with patch("app.services.cohorte_service.BaseRepository") as mock_repo:
        mock_repo.return_value.get_all = AsyncMock(return_value=[])

        response = await async_client.get(
            "/api/v1/admin/cohortes", headers=auth_header
        )
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
async def test_materia_create_returns_201(async_client, auth_header):
    with patch("app.services.materia_service.BaseRepository") as mock_repo:
        mock_instance = Mock()
        mock_instance.id = uuid.uuid4()
        mock_instance.codigo = "MAT01"
        mock_instance.nombre = "Matemáticas"
        mock_instance.descripcion = None
        mock_instance.carrera_id = None
        mock_instance.created_at = datetime.now(timezone.utc)
        mock_instance.updated_at = datetime.now(timezone.utc)
        mock_repo.return_value.create = AsyncMock(return_value=mock_instance)

        response = await async_client.post(
            "/api/v1/admin/materias",
            json={"codigo": "MAT01", "nombre": "Matemáticas"},
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["codigo"] == "MAT01"


@pytest.mark.asyncio
async def test_materia_list_returns_200(async_client, auth_header):
    with patch("app.services.materia_service.BaseRepository") as mock_repo:
        mock_repo.return_value.get_all = AsyncMock(return_value=[])

        response = await async_client.get(
            "/api/v1/admin/materias", headers=auth_header
        )
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
async def test_materia_get_returns_200(async_client, auth_header):
    materia_id = uuid.uuid4()
    mock_instance = Mock()
    mock_instance.id = materia_id
    mock_instance.codigo = "MAT01"
    mock_instance.nombre = "Matemáticas"
    mock_instance.descripcion = None
    mock_instance.carrera_id = None
    mock_instance.created_at = datetime.now(timezone.utc)
    mock_instance.updated_at = datetime.now(timezone.utc)

    with patch("app.services.materia_service.BaseRepository") as mock_repo:
        mock_repo.return_value.get = AsyncMock(return_value=mock_instance)

        response = await async_client.get(
            f"/api/v1/admin/materias/{materia_id}", headers=auth_header
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_unauthorized_returns_401(async_client):
    response = await async_client.get("/api/v1/admin/carreras")
    assert response.status_code == 401
