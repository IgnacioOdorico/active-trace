import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.services.audit_service import audit_log


class FakeUser:
    def __init__(self):
        self.id = uuid.uuid4()
        self.tenant_id = uuid.uuid4()


class FakeHeaders:
    def get(self, key, default=None):
        if key == "user-agent":
            return "test-agent"
        return default


class FakeRequest:
    class Client:
        host = "10.0.0.1"
    client = Client()
    headers = FakeHeaders()


@pytest.fixture
def fake_user():
    return FakeUser()


@pytest.fixture
def fake_request():
    return FakeRequest()


class TestAuditLogDecoratorImpersonation:
    @pytest.mark.asyncio
    async def test_decorator_uses_impersonator_id_when_present(self, fake_user, fake_request):
        fake_user.impersonator_id = str(uuid.uuid4())

        @audit_log(accion="TEST_ACCION")
        async def my_handler(db, current_user, request):
            return {"ok": True}

        with patch("app.services.audit_service.log_action") as mock_log:
            result = await my_handler(
                db=AsyncMock(),
                current_user=fake_user,
                request=fake_request,
            )
            assert result == {"ok": True}
            mock_log.assert_awaited_once()
            call_kwargs = mock_log.call_args[1]
            assert call_kwargs["actor_id"] == uuid.UUID(fake_user.impersonator_id)
            assert call_kwargs["impersonado_id"] == fake_user.id

    @pytest.mark.asyncio
    async def test_decorator_uses_normal_id_when_not_impersonating(self, fake_user, fake_request):
        @audit_log(accion="TEST_ACCION")
        async def my_handler(db, current_user, request):
            return {"ok": True}

        with patch("app.services.audit_service.log_action") as mock_log:
            result = await my_handler(
                db=AsyncMock(),
                current_user=fake_user,
                request=fake_request,
            )
            assert result == {"ok": True}
            mock_log.assert_awaited_once()
            call_kwargs = mock_log.call_args[1]
            assert call_kwargs["actor_id"] == fake_user.id
            assert call_kwargs.get("impersonado_id") is None

    @pytest.mark.asyncio
    async def test_decorator_skips_log_when_no_db(self, fake_user, fake_request):
        @audit_log(accion="TEST_ACCION")
        async def my_handler(request):
            return {"ok": True}

        with patch("app.services.audit_service.log_action") as mock_log:
            result = await my_handler(request=fake_request)
            assert result == {"ok": True}
            mock_log.assert_not_awaited()
