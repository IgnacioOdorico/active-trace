import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_current_user, get_db
from app.main import app
from app.models.user import User


class _MockSession:
    def __init__(self) -> None:
        self.commit = AsyncMock()
        self.execute = AsyncMock()


class TestSalarioBaseRouter:
    """Reproduce el 500 real: el response_model esperaba created_at/updated_at
    como str pero el repositorio devuelve datetime (columnas DateTime del
    modelo). FastAPI valida la respuesta contra el schema antes de serializar
    y, al fallar esa validación, escapa como 500 sin headers de CORS."""

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

    def _mock_entity(self):
        entity = Mock()
        entity.id = uuid.uuid4()
        entity.tenant_id = self._tenant_id
        entity.rol = "PROFESOR"
        entity.monto = 100000.0
        entity.desde = date(2026, 1, 1)
        entity.hasta = None
        entity.created_at = datetime(2026, 6, 18, 2, 35, 8, tzinfo=timezone.utc)
        entity.updated_at = datetime(2026, 6, 18, 2, 35, 8, tzinfo=timezone.utc)
        return entity

    @pytest.mark.asyncio
    async def test_listar_salarios_base_no_crashea_con_datetime_real(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.salario_base.SalarioBaseRepository") as MockRepo,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            MockRepo.return_value.get_all = AsyncMock(return_value=[self._mock_entity()])

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/salario-base",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["created_at"].startswith("2026-06-18")

    @pytest.mark.asyncio
    async def test_obtener_salario_base_no_crashea_con_datetime_real(self):
        entity = self._mock_entity()
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.salario_base.SalarioBaseRepository") as MockRepo,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            MockRepo.return_value.get = AsyncMock(return_value=entity)

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/api/salario-base/{entity.id}",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200


class TestSalarioPlusRouter:
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

    def _mock_entity(self):
        entity = Mock()
        entity.id = uuid.uuid4()
        entity.tenant_id = self._tenant_id
        entity.grupo = "Docencia"
        entity.rol = "PROFESOR"
        entity.descripcion = "Plus por antigüedad"
        entity.monto = 5000.0
        entity.desde = date(2026, 1, 1)
        entity.hasta = None
        entity.created_at = datetime(2026, 6, 18, 6, 4, 2, tzinfo=timezone.utc)
        entity.updated_at = datetime(2026, 6, 18, 6, 4, 2, tzinfo=timezone.utc)
        return entity

    @pytest.mark.asyncio
    async def test_listar_salarios_plus_no_crashea_con_datetime_real(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["ADMIN"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.salario_plus.SalarioPlusRepository") as MockRepo,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            MockRepo.return_value.get_all = AsyncMock(return_value=[self._mock_entity()])

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/api/salario-plus",
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["created_at"].startswith("2026-06-18")
