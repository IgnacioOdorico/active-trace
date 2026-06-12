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


class TestInboxRouter:
    _tenant_id = uuid.uuid4()
    _user_id = uuid.uuid4()
    _other_user_id = uuid.uuid4()
    _root_id = uuid.uuid4()

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

    # --- 7.1 (RED): GET /api/inbox ---

    @pytest.mark.asyncio
    async def test_get_inbox_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["PROFESOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.inbox.InboxService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.listar_hilos = AsyncMock(return_value=(
                [{"id": str(self._root_id), "asunto": "Hola", "ultimo_mensaje": "Cuerpo",
                  "remitente_id": str(self._other_user_id),
                  "destinatario_id": str(self._user_id),
                  "leido": False, "created_at": "2026-06-12T00:00:00"}],
                1,
            ))

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(
                    "/api/inbox",
                    headers={"Authorization": "Bearer fake-token"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["asunto"] == "Hola"

    @pytest.mark.asyncio
    async def test_get_inbox_without_auth_returns_401(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/inbox")

        assert response.status_code == 401

    # --- 7.3 (RED): GET /api/inbox/{id} ---

    @pytest.mark.asyncio
    async def test_get_inbox_hilo_returns_200(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["PROFESOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.inbox.InboxService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.obtener_hilo = AsyncMock(return_value={
                "id": str(self._root_id),
                "asunto": "Hola",
                "cuerpo": "Mensaje raíz",
                "remitente_id": str(self._other_user_id),
                "destinatario_id": str(self._user_id),
                "leido": False,
                "created_at": "2026-06-12T00:00:00",
                "thread_id": None,
                "respuestas": [],
            })

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(
                    f"/api/inbox/{self._root_id}",
                    headers={"Authorization": "Bearer fake-token"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["asunto"] == "Hola"
            assert data["respuestas"] == []

    # --- 7.5 (RED): POST /api/inbox/{id}/responder ---

    @pytest.mark.asyncio
    async def test_responder_creates_reply_201(self):
        with (
            patch("app.core.permissions.decode_access_token", return_value={"rols": ["PROFESOR"]}),
            patch("app.core.permissions.PermissionChecker") as MockPerm,
            patch("app.routers.inbox.InboxService") as MockSvc,
        ):
            MockPerm.return_value.has_permission = AsyncMock(return_value=(True, False))
            mock_svc = MockSvc.return_value
            mock_svc.responder = AsyncMock(return_value={
                "id": str(uuid.uuid4()),
                "thread_id": str(self._root_id),
                "asunto": "Re: Hola",
                "cuerpo": "Mi respuesta",
                "remitente_id": str(self._user_id),
                "destinatario_id": str(self._other_user_id),
                "leido": False,
                "created_at": "2026-06-12T00:00:00",
            })

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    f"/api/inbox/{self._root_id}/responder",
                    json={"cuerpo": "Mi respuesta"},
                    headers={"Authorization": "Bearer fake-token"},
                )

            assert response.status_code == 201
            data = response.json()
            assert data["cuerpo"] == "Mi respuesta"

    # --- 7.7 (TRIANGULATE) ---

    @pytest.mark.asyncio
    async def test_responder_sin_auth_returns_401(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                f"/api/inbox/{self._root_id}/responder",
                json={"cuerpo": "test"},
            )

        assert response.status_code == 401
