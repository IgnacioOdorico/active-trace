import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_current_user, get_db
from app.main import app
from app.models.user import User


class _MockSession:
    def __init__(self) -> None:
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        execute_result = Mock()
        execute_result.scalars.return_value.all.return_value = []
        execute_result.scalar_one_or_none.return_value = None
        execute_result.scalar_one.return_value = 0
        self.execute = AsyncMock(return_value=execute_result)
        self.flush = AsyncMock()
        self.refresh = AsyncMock()
        self.close = AsyncMock()
        self.add = Mock()
        self.get = AsyncMock()
        self.delete = Mock()


class TestAvisosRouters:
    _tenant_id = uuid.uuid4()
    _user_id = uuid.uuid4()
    _aviso_id = uuid.uuid4()

    @pytest.fixture(autouse=True)
    def mock_deps(self):
        async def _mock_user():
            user = Mock(spec=User)
            user.id = self._user_id
            user.tenant_id = self._tenant_id
            user.is_active = True
            user.impersonator_id = None
            return user

        async def _mock_db():
            return _MockSession()

        app.dependency_overrides[get_current_user] = _mock_user
        app.dependency_overrides[get_db] = _mock_db
        yield
        app.dependency_overrides.clear()

    # ---- 8.1: ABM avisos ----

    @pytest.mark.asyncio
    async def test_crear_aviso_exitoso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.crear = AsyncMock(return_value={
                "id": str(self._aviso_id),
                "tenant_id": str(self._tenant_id),
                "alcance": "Global",
                "severidad": "Info",
                "titulo": "Aviso importante",
                "cuerpo": "Contenido del aviso",
                "inicio_en": "2026-06-01T00:00:00+00:00",
                "fin_en": "2026-07-01T00:00:00+00:00",
                "orden": 1,
                "activo": True,
                "requiere_ack": False,
                "materia_id": None,
                "cohorte_id": None,
                "rol_destino": None,
                "created_at": "2026-06-11T00:00:00+00:00",
                "updated_at": "2026-06-11T00:00:00+00:00",
                "total_acks": 0,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/avisos",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Aviso importante",
                        "cuerpo": "Contenido del aviso",
                        "inicio_en": "2026-06-01T00:00:00Z",
                        "fin_en": "2026-07-01T00:00:00Z",
                        "orden": 1,
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 201
                data = response.json()
                assert data["titulo"] == "Aviso importante"
                assert data["alcance"] == "Global"

    @pytest.mark.asyncio
    async def test_crear_aviso_403_sin_permiso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/avisos",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Aviso importante",
                        "cuerpo": "Contenido",
                        "inicio_en": "2026-06-01T00:00:00Z",
                        "fin_en": "2026-07-01T00:00:00Z",
                        "orden": 1,
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_crear_aviso_422_datos_invalidos(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/avisos",
                    json={
                        "alcance": "Global",
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_editar_aviso_exitoso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.editar = AsyncMock(return_value={
                "id": str(self._aviso_id),
                "tenant_id": str(self._tenant_id),
                "alcance": "Global",
                "severidad": "Info",
                "titulo": "Aviso editado",
                "cuerpo": "Contenido editado",
                "inicio_en": "2026-06-01T00:00:00+00:00",
                "fin_en": "2026-07-01T00:00:00+00:00",
                "orden": 2,
                "activo": True,
                "requiere_ack": False,
                "materia_id": None,
                "cohorte_id": None,
                "rol_destino": None,
                "created_at": "2026-06-11T00:00:00+00:00",
                "updated_at": "2026-06-11T00:00:00+00:00",
                "total_acks": 0,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/avisos/{self._aviso_id}",
                    json={"titulo": "Aviso editado", "orden": 2},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["titulo"] == "Aviso editado"

    @pytest.mark.asyncio
    async def test_editar_aviso_inexistente_404(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            from app.core.exceptions import EntityNotFoundError
            mock_svc.editar = AsyncMock(
                side_effect=EntityNotFoundError("Aviso", uuid.uuid4())
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/avisos/{uuid.uuid4()}",
                    json={"titulo": "Editado"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_eliminar_aviso_exitoso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.eliminar = AsyncMock(return_value=None)

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete(
                    f"/api/avisos/{self._aviso_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_eliminar_aviso_inexistente_404(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            from app.core.exceptions import EntityNotFoundError
            mock_svc.eliminar = AsyncMock(
                side_effect=EntityNotFoundError("Aviso", uuid.uuid4())
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete(
                    f"/api/avisos/{uuid.uuid4()}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_eliminar_aviso_403_sin_permiso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete(
                    f"/api/avisos/{self._aviso_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    # ---- 8.2: Visualización por perfil ----

    @pytest.mark.asyncio
    async def test_listar_visibles_exitoso(self):
        aviso_id = str(uuid.uuid4())
        with (
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            mock_svc = MockSvc.return_value
            mock_svc.listar_visibles = AsyncMock(return_value={
                "items": [
                    {
                        "id": aviso_id,
                        "tenant_id": str(self._tenant_id),
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Aviso global",
                        "cuerpo": "Contenido",
                        "inicio_en": "2026-06-01T00:00:00+00:00",
                        "fin_en": "2026-07-01T00:00:00+00:00",
                        "orden": 1,
                        "activo": True,
                        "requiere_ack": False,
                        "materia_id": None,
                        "cohorte_id": None,
                        "rol_destino": None,
                        "created_at": "2026-06-11T00:00:00+00:00",
                        "updated_at": "2026-06-11T00:00:00+00:00",
                        "total_acks": 0,
                    }
                ],
                "total": 1,
                "pagina": 1,
                "page_size": 50,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/avisos",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["total"] == 1
                assert data["items"][0]["alcance"] == "Global"

    @pytest.mark.asyncio
    async def test_listar_visibles_vacio(self):
        with (
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            mock_svc = MockSvc.return_value
            mock_svc.listar_visibles = AsyncMock(return_value={
                "items": [],
                "total": 0,
                "pagina": 1,
                "page_size": 50,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/avisos",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["total"] == 0

    # ---- 8.3: Acknowledgment ----

    @pytest.mark.asyncio
    async def test_confirmar_lectura_exitoso(self):
        with (
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            mock_svc = MockSvc.return_value
            ack_id = uuid.uuid4()
            mock_svc.confirmar_lectura = AsyncMock(return_value={
                "id": str(ack_id),
                "aviso_id": str(self._aviso_id),
                "usuario_id": str(self._user_id),
                "confirmado_at": "2026-06-11T12:00:00+00:00",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/avisos/{self._aviso_id}/ack",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["aviso_id"] == str(self._aviso_id)
                assert data["usuario_id"] == str(self._user_id)

    @pytest.mark.asyncio
    async def test_confirmar_lectura_idempotente(self):
        with (
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            mock_svc = MockSvc.return_value
            mock_svc.confirmar_lectura = AsyncMock(return_value={
                "id": "",
                "aviso_id": str(self._aviso_id),
                "usuario_id": str(self._user_id),
                "confirmado_at": "",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/avisos/{self._aviso_id}/ack",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == ""

    @pytest.mark.asyncio
    async def test_confirmar_lectura_aviso_inexistente_404(self):
        with (
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            mock_svc = MockSvc.return_value
            from app.core.exceptions import EntityNotFoundError
            mock_svc.confirmar_lectura = AsyncMock(
                side_effect=EntityNotFoundError("Aviso", uuid.uuid4())
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/avisos/{uuid.uuid4()}/ack",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 404

    # ---- 8.4: Gestión ----

    @pytest.mark.asyncio
    async def test_listar_gestion_paginado(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_gestion = AsyncMock(return_value={
                "items": [
                    {
                        "id": str(self._aviso_id),
                        "tenant_id": str(self._tenant_id),
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Aviso gestion",
                        "cuerpo": "Contenido",
                        "inicio_en": "2026-06-01T00:00:00+00:00",
                        "fin_en": "2026-07-01T00:00:00+00:00",
                        "orden": 1,
                        "activo": True,
                        "requiere_ack": True,
                        "materia_id": None,
                        "cohorte_id": None,
                        "rol_destino": None,
                        "created_at": "2026-06-11T00:00:00+00:00",
                        "updated_at": "2026-06-11T00:00:00+00:00",
                        "total_acks": 5,
                    }
                ],
                "total": 1,
                "pagina": 1,
                "page_size": 50,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/avisos/gestion",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["total"] == 1
                assert data["items"][0]["total_acks"] == 5

    @pytest.mark.asyncio
    async def test_listar_gestion_403_sin_permiso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/avisos/gestion",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_obtener_aviso_con_contador(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener = AsyncMock(return_value={
                "id": str(self._aviso_id),
                "tenant_id": str(self._tenant_id),
                "alcance": "Global",
                "severidad": "Info",
                "titulo": "Aviso detalle",
                "cuerpo": "Contenido",
                "inicio_en": "2026-06-01T00:00:00+00:00",
                "fin_en": "2026-07-01T00:00:00+00:00",
                "orden": 1,
                "activo": True,
                "requiere_ack": True,
                "materia_id": None,
                "cohorte_id": None,
                "rol_destino": None,
                "created_at": "2026-06-11T00:00:00+00:00",
                "updated_at": "2026-06-11T00:00:00+00:00",
                "total_acks": 3,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/avisos/{self._aviso_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["total_acks"] == 3

    @pytest.mark.asyncio
    async def test_obtener_aviso_inexistente_404(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener = AsyncMock(return_value=None)

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/avisos/{uuid.uuid4()}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 404

    # ---- 8.5: Tests de auditoría ----

    @pytest.mark.asyncio
    async def test_audit_crear_aviso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.avisos.AvisoService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.crear = AsyncMock(return_value={
                "id": str(self._aviso_id),
                "titulo": "Aviso audit",
                "alcance": "Global",
                "severidad": "Info",
                "cuerpo": "Contenido",
                "inicio_en": "2026-06-01T00:00:00+00:00",
                "fin_en": "2026-07-01T00:00:00+00:00",
                "orden": 1,
                "tenant_id": str(self._tenant_id),
                "activo": True,
                "requiere_ack": False,
                "materia_id": None,
                "cohorte_id": None,
                "rol_destino": None,
                "created_at": "2026-06-11T00:00:00+00:00",
                "updated_at": "2026-06-11T00:00:00+00:00",
                "total_acks": 0,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/avisos",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Aviso audit",
                        "cuerpo": "Contenido",
                        "inicio_en": "2026-06-01T00:00:00Z",
                        "fin_en": "2026-07-01T00:00:00Z",
                        "orden": 1,
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 201
