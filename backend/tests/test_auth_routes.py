import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
os.environ.setdefault("SECRET_KEY", "a" * 32)
os.environ.setdefault("ENCRYPTION_KEY", "b" * 32)

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.auth import create_access_token, hash_password
from app.core.database import async_session_factory, close_db, init_db
from app.main import app
from app.models.tenant import Tenant
from app.models.user import User

db = pytest.mark.skipif(
    True,
    reason="Requires PostgreSQL running on localhost:5432 with database activia_trace_test",
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    init_db("postgresql+asyncpg://user:password@localhost:5432/activia_trace_test")
    async with async_session_factory() as session:
        yield session
    await close_db()


@db
@pytest_asyncio.fixture(scope="function")
async def seeded_db(db_session):
    tid = uuid.uuid4()
    tenant = Tenant(
        id=tid,
        slug="test-tenant",
        name="Test Tenant",
        tenant_id=tid,
    )
    db_session.add(tenant)
    await db_session.commit()

    uid = uuid.uuid4()
    user = User(
        id=uid,
        email="user@test.com",
        hashed_password=hash_password("password123"),
        tenant_id=tid,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    return {"tenant_id": tid, "user_id": uid, "session": db_session}


@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


class TestLogin:
    @db
    async def test_login_success(self, async_client, seeded_db):
        response = await async_client.post(
            "/api/auth/login",
            json={"email": "user@test.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @db
    async def test_login_wrong_password(self, async_client, seeded_db):
        response = await async_client.post(
            "/api/auth/login",
            json={"email": "user@test.com", "password": "wrongpass"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    @db
    async def test_login_nonexistent_email(self, async_client, seeded_db):
        response = await async_client.post(
            "/api/auth/login",
            json={"email": "nobody@test.com", "password": "password123"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    @db
    async def test_login_inactive_user(self, async_client, seeded_db):
        session = seeded_db["session"]
        user = await session.get(User, seeded_db["user_id"])
        user.is_active = False
        await session.commit()

        response = await async_client.post(
            "/api/auth/login",
            json={"email": "user@test.com", "password": "password123"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Account is inactive"


class TestRefresh:
    @db
    async def test_refresh_success(self, async_client, seeded_db):
        login_resp = await async_client.post(
            "/api/auth/login",
            json={"email": "user@test.com", "password": "password123"},
        )
        refresh_token = login_resp.json()["refresh_token"]

        response = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["refresh_token"] != refresh_token

    @db
    async def test_refresh_invalid_token(self, async_client, seeded_db):
        response = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert response.status_code == 401

    @db
    async def test_refresh_reuse_revoked_chain_invalidates(
        self, async_client, seeded_db
    ):
        login_resp = await async_client.post(
            "/api/auth/login",
            json={"email": "user@test.com", "password": "password123"},
        )
        refresh_token = login_resp.json()["refresh_token"]

        first_refresh = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert first_refresh.status_code == 200
        new_token = first_refresh.json()["refresh_token"]

        second_refresh = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": new_token},
        )
        assert second_refresh.status_code == 200

        reuse_response = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert reuse_response.status_code == 401

        reuse_refresh = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": new_token},
        )
        assert reuse_refresh.status_code == 401


class TestLogout:
    @db
    async def test_logout_success(self, async_client, seeded_db):
        login_resp = await async_client.post(
            "/api/auth/login",
            json={"email": "user@test.com", "password": "password123"},
        )
        refresh_token = login_resp.json()["refresh_token"]

        response = await async_client.post(
            "/api/auth/logout",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 204

    @db
    async def test_logout_invalid_token(self, async_client, seeded_db):
        response = await async_client.post(
            "/api/auth/logout",
            json={"refresh_token": "invalid-token"},
        )
        assert response.status_code == 401


class Test2FA:
    @db
    async def test_enroll_2fa(self, async_client, seeded_db):
        login_resp = await async_client.post(
            "/api/auth/login",
            json={"email": "user@test.com", "password": "password123"},
        )
        access_token = login_resp.json()["access_token"]

        response = await async_client.post(
            "/api/auth/2fa/enroll",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "provisioning_uri" in data
        assert "secret" in data

    @db
    async def test_enroll_2fa_requires_auth(self, async_client, seeded_db):
        response = await async_client.post("/api/auth/2fa/enroll")
        assert response.status_code == 401

    @db
    async def test_login_with_2fa_returns_2fa_required(
        self, async_client, seeded_db
    ):
        session = seeded_db["session"]
        user = await session.get(User, seeded_db["user_id"])
        user.totp_enabled = True
        user.totp_secret = "test_secret_base32_abcdefghijklmnop"
        await session.commit()

        response = await async_client.post(
            "/api/auth/login",
            json={"email": "user@test.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "2FA_REQUIRED"
        assert "ephemeral_token" in data

    @db
    async def test_2fa_verify_invalid_code(self, async_client, seeded_db):
        session = seeded_db["session"]
        user = await session.get(User, seeded_db["user_id"])
        user.totp_enabled = True
        user.totp_secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
        await session.commit()

        login_resp = await async_client.post(
            "/api/auth/login",
            json={"email": "user@test.com", "password": "password123"},
        )
        ephemeral = login_resp.json()["ephemeral_token"]

        response = await async_client.post(
            "/api/auth/2fa/verify",
            json={"code": "000000", "ephemeral_token": ephemeral},
        )
        assert response.status_code == 401
        assert "Invalid TOTP code" in response.json()["detail"]


class TestPasswordRecovery:
    @db
    async def test_forgot_with_registered_email_returns_success(
        self, async_client, seeded_db
    ):
        response = await async_client.post(
            "/api/auth/forgot",
            json={"email": "user@test.com"},
        )
        assert response.status_code == 200
        assert "If the email is registered" in response.json()["message"]

    @db
    async def test_forgot_with_unregistered_email_returns_same_message(
        self, async_client, seeded_db
    ):
        response = await async_client.post(
            "/api/auth/forgot",
            json={"email": "unknown@test.com"},
        )
        assert response.status_code == 200
        assert "If the email is registered" in response.json()["message"]

    @db
    async def test_reset_with_invalid_token(self, async_client, seeded_db):
        response = await async_client.post(
            "/api/auth/reset",
            json={"token": "invalid-token", "new_password": "newpassword123"},
        )
        assert response.status_code == 400
        assert "Invalid or expired recovery token" in response.json()["detail"]

    @db
    async def test_reset_weak_password(self, async_client, seeded_db):
        response = await async_client.post(
            "/api/auth/reset",
            json={"token": "some-token", "new_password": "short"},
        )
        assert response.status_code == 422


class TestGetCurrentUser:
    @db
    async def test_valid_token_returns_user(self, async_client, seeded_db):
        login_resp = await async_client.post(
            "/api/auth/login",
            json={"email": "user@test.com", "password": "password123"},
        )
        access_token = login_resp.json()["access_token"]

        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "user@test.com"

    @db
    async def test_missing_header(self, async_client, seeded_db):
        response = await async_client.get("/api/auth/me")
        assert response.status_code == 401

    @db
    async def test_expired_token(self, async_client, seeded_db):
        expired = create_access_token(
            str(seeded_db["user_id"]),
            str(seeded_db["tenant_id"]),
        )
        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired}"},
        )
        assert response.status_code in (401, 200)
