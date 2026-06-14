import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import settings

_ph = PasswordHasher()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
EPHEMERAL_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plain)
    except Exception:
        return False


def create_access_token(
    user_id: str,
    tenant_id: str,
    roles: list[str] | None = None,
    impersonating: bool = False,
    impersonator_id: str | None = None,
    impersonated_user_id: str | None = None,
    original_roles: list[str] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    claims: dict = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "rols": roles or [],
        "impersonating": impersonating,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now,
        "type": "access",
    }
    if impersonating:
        if impersonator_id is not None:
            claims["impersonator_id"] = impersonator_id
        if impersonated_user_id is not None:
            claims["impersonated_user_id"] = impersonated_user_id
        if original_roles is not None:
            claims["original_roles"] = original_roles
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") not in ("access", "ephemeral"):
            raise JWTError("Invalid token type")
        return payload
    except ExpiredSignatureError:
        raise
    except JWTError:
        raise JWTError("Invalid token")


def create_refresh_token() -> tuple[str, str]:
    raw = secrets.token_urlsafe(48)
    return raw, hash_token(raw)


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def create_ephemeral_token(user_id: str, tenant_id: str) -> str:
    now = datetime.now(timezone.utc)
    claims = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "exp": now + timedelta(minutes=EPHEMERAL_TOKEN_EXPIRE_MINUTES),
        "iat": now,
        "type": "ephemeral",
        "purpose": "2fa",
    }
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=ALGORITHM)
