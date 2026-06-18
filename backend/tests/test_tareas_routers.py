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


class TestTareasRouters:
    _tenant_id = uuid.uuid4()
    _user_id = uuid.uuid4()
    _tarea_id = uuid.uuid4()
    _otro_user_id = uuid.uuid4()
    _materia_id = uuid.uuid4()

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

    # ---- 8.1: ABM ----

    @pytest.mark.asyncio
    async def test_crear_tarea_exitoso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.crear = AsyncMock(return_value={
                "id": str(self._tarea_id),
                "tenant_id": str(self._tenant_id),
                "materia_id": None,
                "asignado_a": str(self._otro_user_id),
                "asignado_por": str(self._user_id),
                "estado": "Pendiente",
                "descripcion": "Preparar materiales",
                "contexto_id": None,
                "created_at": "2026-06-11T00:00:00+00:00",
                "updated_at": "2026-06-11T00:00:00+00:00",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/tareas",
                    json={
                        "asignado_a": str(self._otro_user_id),
                        "descripcion": "Preparar materiales",
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 201
                data = response.json()
                assert data["estado"] == "Pendiente"
                assert data["descripcion"] == "Preparar materiales"

    @pytest.mark.asyncio
    async def test_listar_asignables_disponible_para_coordinador(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.UsuarioService") as MockUsuarioSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_rol = Mock()
            mock_rol.codigo = "PROFESOR"
            mock_user = Mock()
            mock_user.id = self._otro_user_id
            mock_user.nombre = "Ana"
            mock_user.apellidos = "Gomez"
            mock_user.email = "ana.gomez@example.com"
            mock_user.roles = [mock_rol]
            MockUsuarioSvc.return_value.get_all = AsyncMock(return_value=([mock_user], 1))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/tareas/asignables",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["nombre"] == "Ana"
                assert data[0]["email"] == "ana.gomez@example.com"

    @pytest.mark.asyncio
    async def test_listar_asignables_excluye_alumnos(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.UsuarioService") as MockUsuarioSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            rol_profesor = Mock()
            rol_profesor.codigo = "PROFESOR"
            rol_alumno = Mock()
            rol_alumno.codigo = "ALUMNO"

            mock_profesor = Mock()
            mock_profesor.id = self._otro_user_id
            mock_profesor.nombre = "Ana"
            mock_profesor.apellidos = "Gomez"
            mock_profesor.email = "ana.gomez@example.com"
            mock_profesor.roles = [rol_profesor]

            mock_alumno = Mock()
            mock_alumno.id = uuid.uuid4()
            mock_alumno.nombre = "Alumno"
            mock_alumno.apellidos = "Uno"
            mock_alumno.email = "alumno1@demo.local"
            mock_alumno.roles = [rol_alumno]

            MockUsuarioSvc.return_value.get_all = AsyncMock(
                return_value=([mock_profesor, mock_alumno], 2)
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/tareas/asignables",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["email"] == "ana.gomez@example.com"

    @pytest.mark.asyncio
    async def test_listar_asignables_403_sin_permiso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/tareas/asignables",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_crear_tarea_materia_id_invalido_422(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/tareas",
                    json={
                        "asignado_a": str(self._otro_user_id),
                        "descripcion": "Preparar materiales",
                        "materia_id": "no-es-un-uuid",
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_crear_tarea_asignado_a_invalido_422(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/tareas",
                    json={
                        "asignado_a": "no-es-un-uuid",
                        "descripcion": "Preparar materiales",
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_obtener_tarea_id_invalido_422(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/tareas/no-es-un-uuid",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_crear_tarea_403_sin_permiso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/tareas",
                    json={
                        "asignado_a": str(self._otro_user_id),
                        "descripcion": "Tarea",
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_editar_tarea_asignado_a(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.editar = AsyncMock(return_value={
                "id": str(self._tarea_id),
                "tenant_id": str(self._tenant_id),
                "materia_id": None,
                "asignado_a": str(self._user_id),
                "asignado_por": str(self._otro_user_id),
                "estado": "Pendiente",
                "descripcion": "Reasignada",
                "contexto_id": None,
                "created_at": "2026-06-11T00:00:00+00:00",
                "updated_at": "2026-06-11T00:00:00+00:00",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/tareas/{self._tarea_id}",
                    json={"asignado_a": str(self._user_id)},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["asignado_a"] == str(self._user_id)

    @pytest.mark.asyncio
    async def test_editar_tarea_con_materia_id(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            materia_id = uuid.uuid4()
            mock_svc = MockSvc.return_value
            mock_svc.editar = AsyncMock(return_value={
                "id": str(self._tarea_id),
                "tenant_id": str(self._tenant_id),
                "materia_id": str(materia_id),
                "asignado_a": str(self._user_id),
                "asignado_por": str(self._otro_user_id),
                "estado": "Pendiente",
                "descripcion": "Editada con materia",
                "contexto_id": None,
                "created_at": "2026-06-11T00:00:00+00:00",
                "updated_at": "2026-06-11T00:00:00+00:00",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/tareas/{self._tarea_id}",
                    json={
                        "descripcion": "Editada con materia",
                        "asignado_a": str(self._user_id),
                        "materia_id": str(materia_id),
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["materia_id"] == str(materia_id)

    @pytest.mark.asyncio
    async def test_editar_tarea_inexistente_404(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            from app.core.exceptions import EntityNotFoundError
            mock_svc.editar = AsyncMock(
                side_effect=EntityNotFoundError("Tarea", uuid.uuid4())
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/tareas/{uuid.uuid4()}",
                    json={"descripcion": "Editada"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_eliminar_tarea_204(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.eliminar = AsyncMock(return_value=None)

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete(
                    f"/api/tareas/{self._tarea_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_eliminar_tarea_inexistente_404(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            from app.core.exceptions import EntityNotFoundError
            mock_svc.eliminar = AsyncMock(
                side_effect=EntityNotFoundError("Tarea", uuid.uuid4())
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete(
                    f"/api/tareas/{uuid.uuid4()}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_eliminar_tarea_403_sin_permiso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete(
                    f"/api/tareas/{self._tarea_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    # ---- 8.2: Transiciones de estado ----

    @pytest.mark.asyncio
    async def test_transicion_pendiente_a_en_progreso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.editar = AsyncMock(return_value={
                "id": str(self._tarea_id),
                "tenant_id": str(self._tenant_id),
                "materia_id": None,
                "asignado_a": str(self._user_id),
                "asignado_por": str(self._otro_user_id),
                "estado": "En progreso",
                "descripcion": "Tarea en curso",
                "contexto_id": None,
                "created_at": "2026-06-11T00:00:00+00:00",
                "updated_at": "2026-06-11T00:00:00+00:00",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/tareas/{self._tarea_id}",
                    json={"estado": "En progreso"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["estado"] == "En progreso"

    @pytest.mark.asyncio
    async def test_transicion_pendiente_a_cancelada(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.editar = AsyncMock(return_value={
                "id": str(self._tarea_id),
                "tenant_id": str(self._tenant_id),
                "materia_id": None,
                "asignado_a": str(self._user_id),
                "asignado_por": str(self._otro_user_id),
                "estado": "Cancelada",
                "descripcion": "Tarea cancelada",
                "contexto_id": None,
                "created_at": "2026-06-11T00:00:00+00:00",
                "updated_at": "2026-06-11T00:00:00+00:00",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/tareas/{self._tarea_id}",
                    json={"estado": "Cancelada"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["estado"] == "Cancelada"

    @pytest.mark.asyncio
    async def test_transicion_en_progreso_a_resuelta(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.editar = AsyncMock(return_value={
                "id": str(self._tarea_id),
                "tenant_id": str(self._tenant_id),
                "materia_id": None,
                "asignado_a": str(self._user_id),
                "asignado_por": str(self._otro_user_id),
                "estado": "Resuelta",
                "descripcion": "Tarea resuelta",
                "contexto_id": None,
                "created_at": "2026-06-11T00:00:00+00:00",
                "updated_at": "2026-06-11T00:00:00+00:00",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/tareas/{self._tarea_id}",
                    json={"estado": "Resuelta"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["estado"] == "Resuelta"

    @pytest.mark.asyncio
    async def test_transicion_cancelada_a_pendiente_rechazado(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            from app.core.exceptions import DomainError
            mock_svc.editar = AsyncMock(
                side_effect=DomainError("Transición de estado no permitida: Cancelada → Pendiente")
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/tareas/{self._tarea_id}",
                    json={"estado": "Pendiente"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 400

    # ---- 8.3: Mis tareas ----

    @pytest.mark.asyncio
    async def test_mis_tareas_lista(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["PROFESOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_mias = AsyncMock(return_value={
                "items": [
                    {
                        "id": str(self._tarea_id),
                        "tenant_id": str(self._tenant_id),
                        "materia_id": None,
                        "asignado_a": str(self._user_id),
                        "asignado_por": str(self._otro_user_id),
                        "estado": "Pendiente",
                        "descripcion": "Mi tarea",
                        "contexto_id": None,
                        "created_at": "2026-06-11T00:00:00+00:00",
                        "updated_at": "2026-06-11T00:00:00+00:00",
                    }
                ],
                "total": 1,
                "pagina": 1,
                "page_size": 50,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/tareas/mias",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["total"] == 1
                assert data["items"][0]["descripcion"] == "Mi tarea"

    @pytest.mark.asyncio
    async def test_mis_tareas_filtra_por_estado(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["PROFESOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_mias = AsyncMock(return_value={
                "items": [],
                "total": 0,
                "pagina": 1,
                "page_size": 50,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/tareas/mias?estado=Resuelta",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["total"] == 0

    @pytest.mark.asyncio
    async def test_mis_tareas_vacio(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["PROFESOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_mias = AsyncMock(return_value={
                "items": [],
                "total": 0,
                "pagina": 1,
                "page_size": 50,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/tareas/mias",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["total"] == 0

    # ---- 8.4: Admin ----

    @pytest.mark.asyncio
    async def test_listar_todas_paginado(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_todas = AsyncMock(return_value={
                "items": [
                    {
                        "id": str(self._tarea_id),
                        "tenant_id": str(self._tenant_id),
                        "materia_id": None,
                        "asignado_a": str(self._user_id),
                        "asignado_por": str(self._otro_user_id),
                        "estado": "Pendiente",
                        "descripcion": "Tarea admin",
                        "contexto_id": None,
                        "created_at": "2026-06-11T00:00:00+00:00",
                        "updated_at": "2026-06-11T00:00:00+00:00",
                    }
                ],
                "total": 1,
                "pagina": 1,
                "page_size": 50,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/tareas",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["total"] == 1

    @pytest.mark.asyncio
    async def test_listar_todas_filtro_estado(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_todas = AsyncMock(return_value={
                "items": [],
                "total": 0,
                "pagina": 1,
                "page_size": 50,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/tareas?estado=Pendiente",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_listar_todas_busqueda_libre(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_todas = AsyncMock(return_value={
                "items": [],
                "total": 0,
                "pagina": 1,
                "page_size": 50,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/tareas?busqueda=materiales",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    # ---- 8.5: Comentarios ----

    @pytest.mark.asyncio
    async def test_agregar_comentario_exitoso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["PROFESOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            comentario_id = uuid.uuid4()
            mock_svc.agregar_comentario = AsyncMock(return_value={
                "id": str(comentario_id),
                "tarea_id": str(self._tarea_id),
                "autor_id": str(self._user_id),
                "texto": "Estoy trabajando en esto",
                "creado_at": "2026-06-11T12:00:00+00:00",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/tareas/{self._tarea_id}/comentarios",
                    json={"texto": "Estoy trabajando en esto"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["texto"] == "Estoy trabajando en esto"
                assert data["tarea_id"] == str(self._tarea_id)

    @pytest.mark.asyncio
    async def test_listar_comentarios_tarea(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["PROFESOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            comentario_id = uuid.uuid4()
            mock_svc.listar_comentarios = AsyncMock(return_value={
                "items": [
                    {
                        "id": str(comentario_id),
                        "tarea_id": str(self._tarea_id),
                        "autor_id": str(self._user_id),
                        "texto": "Primer comentario",
                        "creado_at": "2026-06-11T12:00:00+00:00",
                    }
                ],
                "total": 1,
                "pagina": 1,
                "page_size": 50,
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/tareas/{self._tarea_id}/comentarios",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["total"] == 1
                assert data["items"][0]["texto"] == "Primer comentario"

    @pytest.mark.asyncio
    async def test_comentar_tarea_403_sin_permiso(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ALUMNO"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(False, False))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/tareas/{self._tarea_id}/comentarios",
                    json={"texto": "Intruso"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_comentar_tarea_404_inexistente(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            from app.core.exceptions import EntityNotFoundError
            mock_svc.agregar_comentario = AsyncMock(
                side_effect=EntityNotFoundError("Tarea", uuid.uuid4())
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/tareas/{uuid.uuid4()}/comentarios",
                    json={"texto": "Texto"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 404

    # ---- 8.6: Tests de auditoría ----

    @pytest.mark.asyncio
    async def test_audit_crear_tarea(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.crear = AsyncMock(return_value={
                "id": str(self._tarea_id),
                "tenant_id": str(self._tenant_id),
                "materia_id": None,
                "asignado_a": str(self._otro_user_id),
                "asignado_por": str(self._user_id),
                "estado": "Pendiente",
                "descripcion": "Tarea audit",
                "contexto_id": None,
                "created_at": "2026-06-11T00:00:00+00:00",
                "updated_at": "2026-06-11T00:00:00+00:00",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/tareas",
                    json={
                        "asignado_a": str(self._otro_user_id),
                        "descripcion": "Tarea audit",
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_audit_editar_tarea(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.editar = AsyncMock(return_value={
                "id": str(self._tarea_id),
                "tenant_id": str(self._tenant_id),
                "materia_id": None,
                "asignado_a": str(self._otro_user_id),
                "asignado_por": str(self._user_id),
                "estado": "Pendiente",
                "descripcion": "Editada audit",
                "contexto_id": None,
                "created_at": "2026-06-11T00:00:00+00:00",
                "updated_at": "2026-06-11T00:00:00+00:00",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/tareas/{self._tarea_id}",
                    json={"descripcion": "Editada audit"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_audit_comentar_tarea(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["COORDINADOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.tareas.TareaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            comentario_id = uuid.uuid4()
            mock_svc.agregar_comentario = AsyncMock(return_value={
                "id": str(comentario_id),
                "tarea_id": str(self._tarea_id),
                "autor_id": str(self._user_id),
                "texto": "Comentario audit",
                "creado_at": "2026-06-11T12:00:00+00:00",
            })

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/api/tareas/{self._tarea_id}/comentarios",
                    json={"texto": "Comentario audit"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
