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


class TestPerfilRouter:
    _tenant_id = uuid.uuid4()
    _user_id = uuid.uuid4()

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

    # --- 6.1 (RED): GET /api/perfil ---

    @pytest.mark.asyncio
    async def test_get_perfil_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.perfil.PerfilService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener = AsyncMock(return_value={
                "id": str(self._user_id),
                "tenant_id": str(self._tenant_id),
                "email": "user@test.com",
                "nombre": "Juan",
                "apellidos": "Pérez",
                "cuil": "20123456789",
                "cbu": "0000000000000000000000",
                "banco": "Banco Nación",
                "regional": "CABA",
                "estado": "Activo",
                "is_active": True,
                "facturador": False,
                "legajo": None,
                "legajo_profesional": None,
                "alias_cbu": None,
                "dni": "12345678",
                "created_at": None,
                "updated_at": None,
            })

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(
                    "/api/perfil",
                    headers={"Authorization": "Bearer fake-token"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "user@test.com"
            assert data["nombre"] == "Juan"

    # --- 6.3 (RED): PUT /api/perfil ---

    @pytest.mark.asyncio
    async def test_put_perfil_updates_fields(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.perfil.PerfilService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.actualizar = AsyncMock(return_value={
                "id": str(self._user_id),
                "tenant_id": str(self._tenant_id),
                "email": "nuevo@test.com",
                "nombre": "NuevoNombre",
                "apellidos": "Pérez",
                "estado": "Activo",
                "is_active": True,
                "facturador": False,
                "cuil": "20123456789",
                "cbu": None,
                "banco": None,
                "regional": None,
                "legajo": None,
                "legajo_profesional": None,
                "alias_cbu": None,
                "dni": None,
                "created_at": None,
                "updated_at": None,
            })

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put(
                    "/api/perfil",
                    json={"nombre": "NuevoNombre", "email": "nuevo@test.com"},
                    headers={"Authorization": "Bearer fake-token"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["nombre"] == "NuevoNombre"
            assert data["email"] == "nuevo@test.com"

    # --- 6.5 (TRIANGULATE): PUT /api/perfil with cuil returns 422 ---

    @pytest.mark.asyncio
    async def test_put_perfil_with_cuil_in_body_returns_422(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put(
                    "/api/perfil",
                    json={"nombre": "Test", "cuil": "20123456789"},
                    headers={"Authorization": "Bearer fake-token"},
                )

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_put_perfil_without_auth_returns_401(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.put(
                "/api/perfil",
                json={"nombre": "Test"},
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_perfil_without_auth_returns_401(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/perfil")

        assert response.status_code == 401
