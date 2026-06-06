import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
os.environ.setdefault("SECRET_KEY", "a" * 32)
os.environ.setdefault("ENCRYPTION_KEY", "b" * 32)

import pytest
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.auth import (
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_ephemeral_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.core.config import settings


class TestPasswordHashing:
    def test_hash_password_returns_non_plaintext(self):
        h = hash_password("test123")
        assert h != "test123"
        assert h.startswith("$argon2id$")

    def test_verify_password_correct(self):
        h = hash_password("secure-password")
        assert verify_password("secure-password", h) is True

    def test_verify_password_wrong(self):
        h = hash_password("secure-password")
        assert verify_password("wrong-password", h) is False

    def test_verify_password_empty_string(self):
        h = hash_password("something")
        assert verify_password("", h) is False

    def test_same_password_different_hashes(self):
        h1 = hash_password("same-password")
        h2 = hash_password("same-password")
        assert h1 != h2

    def test_hash_and_verify_round_trip(self):
        passwords = ["abc", "unicodeñöü", "a" * 100, "!@#$%^&*()"]
        for pwd in passwords:
            h = hash_password(pwd)
            assert verify_password(pwd, h) is True


class TestJWTToken:
    def test_create_access_token_returns_string(self):
        token = create_access_token("user-1", "tenant-1")
        assert isinstance(token, str)
        assert token.count(".") == 2

    def test_decode_valid_token(self):
        token = create_access_token("user-1", "tenant-1", ["admin"])
        payload = decode_access_token(token)
        assert payload["sub"] == "user-1"
        assert payload["tenant_id"] == "tenant-1"
        assert payload["rols"] == ["admin"]
        assert payload["type"] == "access"

    def test_decode_token_without_roles(self):
        token = create_access_token("user-1", "tenant-1")
        payload = decode_access_token(token)
        assert payload["rols"] == []

    def test_decode_token_has_exp_and_iat(self):
        token = create_access_token("user-1", "tenant-1")
        payload = decode_access_token(token)
        assert "exp" in payload
        assert "iat" in payload
        exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat_dt = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        assert exp_dt > iat_dt
        assert exp_dt - iat_dt <= timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES + 1)

    def test_decode_expired_token_raises(self):
        payload = {
            "sub": "user-1",
            "tenant_id": "tenant-1",
            "roles": [],
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "type": "access",
        }
        expired = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
        with pytest.raises(ExpiredSignatureError):
            decode_access_token(expired)

    def test_decode_invalid_signature_raises(self):
        token = create_access_token("user-1", "tenant-1")
        tampered_token = token.rsplit(".", 1)[0] + ".invalidsignature"
        with pytest.raises(JWTError):
            decode_access_token(tampered_token)

    def test_decode_invalid_token_type_raises(self):
        payload = {
            "sub": "user-1",
            "tenant_id": "tenant-1",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
            "type": "unknown",
        }
        bad_type = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
        with pytest.raises(JWTError):
            decode_access_token(bad_type)

    def test_decode_garbage_token_raises(self):
        with pytest.raises(JWTError):
            decode_access_token("not.a.token")

    def test_decode_empty_string_raises(self):
        with pytest.raises(JWTError):
            decode_access_token("")


class TestEphemeralToken:
    def test_create_ephemeral_token(self):
        token = create_ephemeral_token("user-1", "tenant-1")
        assert isinstance(token, str)
        assert token.count(".") == 2

    def test_decode_ephemeral_token(self):
        token = create_ephemeral_token("user-1", "tenant-1")
        payload = decode_access_token(token)
        assert payload["sub"] == "user-1"
        assert payload["tenant_id"] == "tenant-1"
        assert payload["purpose"] == "2fa"
        assert payload["type"] == "ephemeral"

    def test_ephemeral_token_has_short_expiry(self):
        token = create_ephemeral_token("user-1", "tenant-1")
        payload = decode_access_token(token)
        exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat_dt = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        assert exp_dt - iat_dt <= timedelta(minutes=6)


class TestRefreshToken:
    def test_create_refresh_token_returns_pair(self):
        raw, hashed = create_refresh_token()
        assert isinstance(raw, str)
        assert isinstance(hashed, str)
        assert len(raw) > 32
        assert len(hashed) == 64

    def test_refresh_token_hash_is_sha256(self):
        raw, hashed = create_refresh_token()
        assert hash_token(raw) == hashed

    def test_refresh_token_raw_url_safe(self):
        raw, _ = create_refresh_token()
        assert raw.isprintable()
        assert "+" not in raw
        assert "/" not in raw

    def test_consecutive_tokens_different(self):
        r1, h1 = create_refresh_token()
        r2, h2 = create_refresh_token()
        assert r1 != r2
        assert h1 != h2


class TestHashToken:
    def test_hash_token_returns_hex_string(self):
        h = hash_token("test-token")
        assert isinstance(h, str)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_hash_token_deterministic(self):
        assert hash_token("same") == hash_token("same")

    def test_hash_token_different_for_different_inputs(self):
        assert hash_token("token-a") != hash_token("token-b")


class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_not_rate_limited_below_limit(self):
        from app.core.rate_limiter import RateLimiter

        rl = RateLimiter(max_attempts=5, window_seconds=60)
        for _ in range(4):
            await rl.record_attempt("ip:email@test.com")
        assert await rl.is_rate_limited("ip:email@test.com") is False

    @pytest.mark.asyncio
    async def test_rate_limited_at_limit(self):
        from app.core.rate_limiter import RateLimiter

        rl = RateLimiter(max_attempts=3, window_seconds=60)
        for _ in range(3):
            await rl.record_attempt("ip:limit@test.com")
        assert await rl.is_rate_limited("ip:limit@test.com") is True

    @pytest.mark.asyncio
    async def test_clear_resets_counter(self):
        from app.core.rate_limiter import RateLimiter

        rl = RateLimiter(max_attempts=3, window_seconds=60)
        for _ in range(3):
            await rl.record_attempt("ip:clear@test.com")
        assert await rl.is_rate_limited("ip:clear@test.com") is True
        await rl.clear("ip:clear@test.com")
        assert await rl.is_rate_limited("ip:clear@test.com") is False

    @pytest.mark.asyncio
    async def test_separate_keys_independent(self):
        from app.core.rate_limiter import RateLimiter

        rl = RateLimiter(max_attempts=3, window_seconds=60)
        for _ in range(3):
            await rl.record_attempt("ip:user1@test.com")
        assert await rl.is_rate_limited("ip:user1@test.com") is True
        assert await rl.is_rate_limited("ip:user2@test.com") is False

    @pytest.mark.asyncio
    async def test_window_expiration(self):
        from app.core.rate_limiter import RateLimiter

        rl = RateLimiter(max_attempts=3, window_seconds=0)
        await rl.record_attempt("ip:win@test.com")
        assert await rl.is_rate_limited("ip:win@test.com") is False
