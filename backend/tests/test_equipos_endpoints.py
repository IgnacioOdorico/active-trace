import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import EntityNotFoundError
from app.main import app
from app.models.user import User


class _MockSession:
    """AsyncSession mock that supports await commit/rollback."""

    def __init__(self):
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        self.execute = AsyncMock()
        self.flush = AsyncMock()
        self.refresh = AsyncMock()
        self.close = AsyncMock()
        self.add = MagicMock()


@pytest.fixture(autouse=True)
def mock_deps():
    """Override get_current_user and get_db for all tests."""
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()

    async def _mock_user():
        user = Mock(spec=User)
        user.id = user_id
        user.tenant_id = tenant_id
        user.is_active = True
        user.impersonator_id = None
        return user

    async def _mock_db():
        return _MockSession()

    app.dependency_overrides[get_current_user] = _mock_user
    app.dependency_overrides[get_db] = _mock_db
    yield user_id, tenant_id
    app.dependency_overrides.clear()


@pytest.fixture
def async_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


def _make_mock_asignacion(asignacion_id=None, **overrides):
    aid = asignacion_id or uuid.uuid4()
    now = datetime.now(timezone.utc)
    a = Mock()
    a.id = aid
    a.tenant_id = uuid.uuid4()
    a.usuario_id = uuid.uuid4()
    a.rol = "PROFESOR"
    a.materia_id = uuid.uuid4()
    a.carrera_id = None
    a.cohorte_id = uuid.uuid4()
    a.comisiones = ["A", "B"]
    a.responsable_id = None
    a.desde = now - timedelta(days=30)
    a.hasta = now + timedelta(days=30)
    a.estado_vigencia = "Vigente"
    a.created_at = now
    a.updated_at = now
    for k, v in overrides.items():
        setattr(a, k, v)
    return a


@contextmanager
def _auth_patches(user_id: uuid.UUID, tenant_id: uuid.UUID):
    with patch(
        "app.core.permissions.decode_access_token",
        return_value={
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "rols": ["COORDINADOR"],
        },
    ):
        with patch(
            "app.core.permissions.PermissionChecker.has_permission",
            new=AsyncMock(return_value=(True, False)),
        ):
            yield


AUTH_HEADER = {"Authorization": "Bearer test-token"}


class TestMisEquipos:
    @pytest.mark.asyncio
    async def test_mis_equipos_returns_200(self, async_client, mock_deps):
        user_id, _ = mock_deps
        mock_a = _make_mock_asignacion(usuario_id=user_id)

        with _auth_patches(user_id, uuid.uuid4()):
            with patch("app.routers.equipos.EquipoService") as mock_svc_cls:
                mock_svc = mock_svc_cls.return_value
                mock_svc.listar_mis_equipos = AsyncMock(return_value=[mock_a])

                response = await async_client.get(
                    "/api/equipos/mis-equipos", headers=AUTH_HEADER
                )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 1
        assert data["total"] == 1
        assert data["data"][0]["estado_vigencia"] == "Vigente"
        mock_svc.listar_mis_equipos.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_mis_equipos_filters_by_materia(self, async_client, mock_deps):
        user_id, _ = mock_deps
        materia_id = uuid.uuid4()
        mock_a = _make_mock_asignacion(usuario_id=user_id, materia_id=materia_id)

        with _auth_patches(user_id, uuid.uuid4()):
            with patch("app.routers.equipos.EquipoService") as mock_svc_cls:
                mock_svc = mock_svc_cls.return_value
                mock_svc.listar_mis_equipos = AsyncMock(return_value=[mock_a])

                response = await async_client.get(
                    f"/api/equipos/mis-equipos?materia_id={materia_id}",
                    headers=AUTH_HEADER,
                )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["materia_id"] == str(materia_id)

    @pytest.mark.asyncio
    async def test_mis_equipos_returns_401_without_auth(self, async_client, mock_deps):
        response = await async_client.get("/api/equipos/mis-equipos")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_mis_equipos_returns_403_without_permission(
        self, async_client, mock_deps
    ):
        user_id, tenant_id = mock_deps

        with patch(
            "app.core.permissions.decode_access_token",
            return_value={
                "sub": str(user_id),
                "tenant_id": str(tenant_id),
                "rols": [],
            },
        ):
            response = await async_client.get(
                "/api/equipos/mis-equipos", headers=AUTH_HEADER
            )

        assert response.status_code == 403


class TestAsignacionMasiva:
    @pytest.mark.asyncio
    async def test_asignacion_masiva_returns_201(self, async_client, mock_deps):
        user_id, _ = mock_deps
        uid1, uid2, uid3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        ids_creados = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]

        with _auth_patches(user_id, uuid.uuid4()):
            with patch("app.routers.equipos.EquipoService") as mock_svc_cls:
                mock_svc = mock_svc_cls.return_value
                mock_svc.asignacion_masiva = AsyncMock(return_value=ids_creados)

                response = await async_client.post(
                    "/api/equipos/asignacion-masiva",
                    json={
                        "usuario_ids": [str(uid1), str(uid2), str(uid3)],
                        "rol": "PROFESOR",
                        "materia_id": str(uuid.uuid4()),
                        "carrera_id": str(uuid.uuid4()),
                        "cohorte_id": str(uuid.uuid4()),
                        "comisiones": ["A", "B"],
                        "desde": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    },
                    headers=AUTH_HEADER,
                )

        assert response.status_code == 201
        data = response.json()
        assert "ids_creados" in data
        assert len(data["ids_creados"]) == 3

    @pytest.mark.asyncio
    async def test_asignacion_masiva_invalid_usuario_returns_422(
        self, async_client, mock_deps
    ):
        user_id, _ = mock_deps

        with _auth_patches(user_id, uuid.uuid4()):
            with patch("app.routers.equipos.EquipoService") as mock_svc_cls:
                mock_svc = mock_svc_cls.return_value
                mock_svc.asignacion_masiva = AsyncMock(
                    side_effect=IntegrityError(
                        "INSERT INTO asignaciones", {}, ValueError("FK violation")
                    )
                )

                response = await async_client.post(
                    "/api/equipos/asignacion-masiva",
                    json={
                        "usuario_ids": [str(uuid.uuid4())],
                        "rol": "PROFESOR",
                        "materia_id": str(uuid.uuid4()),
                        "carrera_id": str(uuid.uuid4()),
                        "cohorte_id": str(uuid.uuid4()),
                        "desde": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    },
                    headers=AUTH_HEADER,
                )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_asignacion_masiva_sin_permiso_returns_403(
        self, async_client, mock_deps
    ):
        user_id, tenant_id = mock_deps

        with patch(
            "app.core.permissions.decode_access_token",
            return_value={
                "sub": str(user_id),
                "tenant_id": str(tenant_id),
                "rols": [],
            },
        ):
            response = await async_client.post(
                "/api/equipos/asignacion-masiva",
                json={
                    "usuario_ids": [str(uuid.uuid4())],
                    "rol": "PROFESOR",
                    "materia_id": str(uuid.uuid4()),
                    "carrera_id": str(uuid.uuid4()),
                    "cohorte_id": str(uuid.uuid4()),
                    "desde": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                },
                headers=AUTH_HEADER,
            )

        assert response.status_code == 403


class TestClonarEquipo:
    @pytest.mark.asyncio
    async def test_clonar_returns_201(self, async_client, mock_deps):
        user_id, _ = mock_deps
        ids_creados = [uuid.uuid4(), uuid.uuid4()]

        with _auth_patches(user_id, uuid.uuid4()):
            with patch("app.routers.equipos.EquipoService") as mock_svc_cls:
                mock_svc = mock_svc_cls.return_value
                mock_svc.clonar_equipo = AsyncMock(return_value=ids_creados)

                response = await async_client.post(
                    "/api/equipos/clonar",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "cohorte_origen_id": str(uuid.uuid4()),
                        "cohorte_destino_id": str(uuid.uuid4()),
                        "desde": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                        "hasta": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                    },
                    headers=AUTH_HEADER,
                )

        assert response.status_code == 201
        data = response.json()
        assert "ids_creados" in data
        assert len(data["ids_creados"]) == 2

    @pytest.mark.asyncio
    async def test_clonar_empty_source_returns_200(self, async_client, mock_deps):
        user_id, _ = mock_deps

        with _auth_patches(user_id, uuid.uuid4()):
            with patch("app.routers.equipos.EquipoService") as mock_svc_cls:
                mock_svc = mock_svc_cls.return_value
                mock_svc.clonar_equipo = AsyncMock(return_value=[])

                response = await async_client.post(
                    "/api/equipos/clonar",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "cohorte_origen_id": str(uuid.uuid4()),
                        "cohorte_destino_id": str(uuid.uuid4()),
                        "desde": datetime.now(timezone.utc).isoformat(),
                    },
                    headers=AUTH_HEADER,
                )

        assert response.status_code == 200
        data = response.json()
        assert data["ids_creados"] == []


class TestModificarVigencia:
    @pytest.mark.asyncio
    async def test_modificar_vigencia_individual_returns_200(
        self, async_client, mock_deps
    ):
        user_id, _ = mock_deps
        asignacion_id = uuid.uuid4()
        mock_a = _make_mock_asignacion(asignacion_id=asignacion_id)

        with _auth_patches(user_id, uuid.uuid4()):
            with patch("app.routers.equipos.EquipoService") as mock_svc_cls:
                mock_svc = mock_svc_cls.return_value
                mock_svc.modificar_vigencia = AsyncMock(return_value=mock_a)

                response = await async_client.patch(
                    f"/api/equipos/{asignacion_id}/vigencia",
                    json={
                        "hasta": (
                            datetime.now(timezone.utc) + timedelta(days=60)
                        ).isoformat()
                    },
                    headers=AUTH_HEADER,
                )

        assert response.status_code == 200
        data = response.json()
        assert data["estado_vigencia"] == "Vigente"

    @pytest.mark.asyncio
    async def test_modificar_vigencia_masiva_returns_200(
        self, async_client, mock_deps
    ):
        user_id, _ = mock_deps

        with _auth_patches(user_id, uuid.uuid4()):
            with patch("app.routers.equipos.EquipoService") as mock_svc_cls:
                mock_svc = mock_svc_cls.return_value
                mock_svc.modificar_vigencia_masiva = AsyncMock(return_value=5)

                response = await async_client.patch(
                    "/api/equipos/vigencia-masiva",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "cohorte_id": str(uuid.uuid4()),
                        "hasta": (
                            datetime.now(timezone.utc) + timedelta(days=60)
                        ).isoformat(),
                    },
                    headers=AUTH_HEADER,
                )

        assert response.status_code == 200
        data = response.json()
        assert data["filas_afectadas"] == 5

    @pytest.mark.asyncio
    async def test_modificar_vigencia_not_found_returns_404(
        self, async_client, mock_deps
    ):
        user_id, _ = mock_deps

        with _auth_patches(user_id, uuid.uuid4()):
            with patch("app.routers.equipos.EquipoService") as mock_svc_cls:
                mock_svc = mock_svc_cls.return_value
                mock_svc.modificar_vigencia = AsyncMock(
                    side_effect=EntityNotFoundError(
                        entity_type="Asignacion", entity_id=uuid.uuid4()
                    )
                )

                response = await async_client.patch(
                    f"/api/equipos/{uuid.uuid4()}/vigencia",
                    json={"hasta": datetime.now(timezone.utc).isoformat()},
                    headers=AUTH_HEADER,
                )

        assert response.status_code == 404


class TestExportarEquipo:
    @pytest.mark.asyncio
    async def test_exportar_returns_xlsx(self, async_client, mock_deps):
        user_id, _ = mock_deps
        asignacion_id = uuid.uuid4()
        xlsx_content = b"fake-xlsx-content"

        with _auth_patches(user_id, uuid.uuid4()):
            with patch("app.routers.equipos.EquipoService") as mock_svc_cls:
                mock_svc = mock_svc_cls.return_value
                mock_svc.exportar_equipo = AsyncMock(return_value=xlsx_content)

                response = await async_client.get(
                    f"/api/equipos/{asignacion_id}/exportar",
                    headers=AUTH_HEADER,
                )

        assert response.status_code == 200
        assert (
            response.headers.get("content-type")
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert "Content-Disposition" in response.headers
        assert response.content == xlsx_content



