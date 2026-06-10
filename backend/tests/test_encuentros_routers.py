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


class TestEncuentroRouters:
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
    async def test_post_slots_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.encuentros.EncuentroService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.crear_slot_recurrente = AsyncMock(return_value={"id": str(uuid.uuid4()), "instancias_generadas": 8})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/encuentros/slots",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "titulo": "Clase 1",
                        "hora": "14:00",
                        "dia_semana": "Miércoles",
                        "fecha_inicio": "2026-04-01",
                        "cant_semanas": 8,
                        "meet_url": "https://meet.google.com/abc",
                        "vig_desde": "2026-04-01",
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_post_instancias_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.encuentros.EncuentroService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.crear_encuentro_unico = AsyncMock(return_value={"id": str(uuid.uuid4())})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/encuentros/instancias",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "fecha": "2026-05-01",
                        "hora": "10:00",
                        "titulo": "Clase única",
                        "meet_url": "https://meet.google.com/xyz",
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_patch_instancias_returns_200(self):
        instancia_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.encuentros.EncuentroService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.editar_instancia = AsyncMock(return_value={"id": instancia_id, "estado": "Realizado"})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/encuentros/instancias/{instancia_id}",
                    json={"estado": "Realizado", "video_url": "https://youtube.com/abc"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_html_returns_200(self):
        materia_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.encuentros.EncuentroService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.generar_html = AsyncMock(return_value={"html": "<p>No hay encuentros programados</p>"})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/encuentros/html/{materia_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                assert response.json()["html"] == "<p>No hay encuentros programados</p>"

    @pytest.mark.asyncio
    async def test_get_instancias_list_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.encuentros.EncuentroService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar = AsyncMock(return_value={"items": [], "total": 0, "pagina": 1, "page_size": 50})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/encuentros/instancias",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_sin_permiso_returns_403(self):
        with patch("app.core.permissions.decode_access_token", return_value={"rols": []}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/encuentros/instancias",
                    headers={"Authorization": "Bearer no-perms"},
                )
                assert response.status_code == 403


class TestGuardiaRouters:
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
    async def test_post_guardias_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.guardias.GuardiaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.crear = AsyncMock(return_value={"id": str(uuid.uuid4())})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/guardias",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "carrera_id": str(uuid.uuid4()),
                        "dia": "Lunes",
                        "horario": "14:00–14:45",
                    },
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_guardias_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.guardias.GuardiaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_todas = AsyncMock(return_value={"items": [], "total": 0, "pagina": 1, "page_size": 50})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/guardias",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_patch_guardias_returns_200(self):
        guardia_id = str(uuid.uuid4())
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.guardias.GuardiaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.editar = AsyncMock(return_value={"id": guardia_id, "estado": "Realizada"})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.patch(
                    f"/api/guardias/{guardia_id}",
                    json={"estado": "Realizada"},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_exportar_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.guardias.GuardiaService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.exportar = AsyncMock(return_value={"items": []})

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/guardias/exportar",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_sin_permiso_returns_403(self):
        with patch("app.core.permissions.decode_access_token", return_value={"rols": []}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/guardias",
                    headers={"Authorization": "Bearer no-perms"},
                )
                assert response.status_code == 403
