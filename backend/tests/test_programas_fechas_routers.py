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
        self.execute = AsyncMock(return_value=execute_result)
        self.flush = AsyncMock()
        self.refresh = AsyncMock()
        self.close = AsyncMock()
        self.add = Mock()
        self.get = AsyncMock()


class TestProgramasRouters:
    @pytest.fixture(autouse=True)
    def mock_deps(self):
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
        yield
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_post_programa_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.programas.ProgramaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.crear = AsyncMock(return_value={"id": str(uuid.uuid4())})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/programas",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "carrera_id": str(uuid.uuid4()),
                        "cohorte_id": str(uuid.uuid4()),
                        "titulo": "Programa 2026",
                        "referencia_archivo": "s3://bucket/prog.pdf",
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_programas_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.programas.ProgramaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar = AsyncMock(return_value={"items": [], "total": 0})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/programas",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_programa_by_id_returns_200(self):
        programa_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.programas.ProgramaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener = AsyncMock(return_value={"id": programa_id, "titulo": "Programa 2026"})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/programas/{programa_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["titulo"] == "Programa 2026"

    @pytest.mark.asyncio
    async def test_get_programa_not_found_returns_404(self):
        programa_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.programas.ProgramaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            from app.core.exceptions import EntityNotFoundError
            mock_svc.obtener = AsyncMock(side_effect=EntityNotFoundError("ProgramaMateria", uuid.UUID(programa_id)))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/programas/{programa_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_patch_programa_returns_200(self):
        programa_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.programas.ProgramaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.editar = AsyncMock(return_value={"id": programa_id})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/programas/{programa_id}",
                    json={"titulo": "Nuevo"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_programa_returns_204(self):
        programa_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.programas.ProgramaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.eliminar = AsyncMock()

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete(
                    f"/api/programas/{programa_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_sin_permiso_returns_403(self):
        with patch("app.core.permissions.decode_access_token", return_value={"rols": []}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/programas",
                    headers={"Authorization": "Bearer no-perms"},
                )
                assert response.status_code == 403


class TestFechasAcademicasRouters:
    @pytest.fixture(autouse=True)
    def mock_deps(self):
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
        yield
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_post_fecha_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.fechas_academicas.FechaAcademicaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.crear = AsyncMock(return_value={"id": str(uuid.uuid4())})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/fechas-academicas",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "cohorte_id": str(uuid.uuid4()),
                        "tipo": "Parcial",
                        "numero": 1,
                        "periodo": "2026-1",
                        "fecha": "2026-05-15",
                        "titulo": "Primer Parcial",
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_fechas_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.fechas_academicas.FechaAcademicaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar = AsyncMock(return_value={"items": [], "total": 0})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/fechas-academicas",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_fecha_by_id_returns_200(self):
        fecha_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.fechas_academicas.FechaAcademicaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener = AsyncMock(return_value={"id": fecha_id, "tipo": "Parcial"})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/fechas-academicas/{fecha_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_fecha_not_found_returns_404(self):
        fecha_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.fechas_academicas.FechaAcademicaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            from app.core.exceptions import EntityNotFoundError
            mock_svc.obtener = AsyncMock(side_effect=EntityNotFoundError("FechaAcademica", uuid.UUID(fecha_id)))

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/fechas-academicas/{fecha_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_patch_fecha_returns_200(self):
        fecha_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.fechas_academicas.FechaAcademicaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.editar = AsyncMock(return_value={"id": fecha_id})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/fechas-academicas/{fecha_id}",
                    json={"titulo": "Cambio"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_fecha_returns_204(self):
        fecha_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.fechas_academicas.FechaAcademicaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.eliminar = AsyncMock()

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete(
                    f"/api/fechas-academicas/{fecha_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_get_lms_fragmento_returns_200(self):
        materia_id = str(uuid.uuid4())
        cohorte_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.fechas_academicas.FechaAcademicaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.generar_fragmento_lms = AsyncMock(
                return_value={"html": "<table class=\"fechas-academicas\"><tr><td>test</td></tr></table>"}
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/fechas-academicas/lms/{materia_id}/{cohorte_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert "fechas-academicas" in response.json()["html"]

    @pytest.mark.asyncio
    async def test_sin_permiso_returns_403(self):
        with patch("app.core.permissions.decode_access_token", return_value={"rols": []}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/fechas-academicas",
                    headers={"Authorization": "Bearer no-perms"},
                )
                assert response.status_code == 403
