import uuid
from datetime import datetime, timedelta, timezone

import pyotp
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from jose import ExpiredSignatureError, JWTError
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_ephemeral_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.core.dependencies import get_current_user, get_db
from app.core.rate_limiter import rate_limiter
from app.models.recovery_token import RecoveryToken
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import (
    ForgotRequest,
    Login2FARequired,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    ResetRequest,
    TOTPEnrollResponse,
    TOTPVerifyRequest,
    TokenResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(
    request: LoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    ip = req.client.host if req.client else "unknown"
    key = f"{ip}:{request.email}"

    if await rate_limiter.is_rate_limited(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )

    await rate_limiter.record_attempt(key)

    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is inactive")

    await rate_limiter.clear(key)

    if user.totp_enabled:
        ephemeral = create_ephemeral_token(str(user.id), str(user.tenant_id))
        return Login2FARequired(status="2FA_REQUIRED", ephemeral_token=ephemeral)

    role_cods = [r.codigo for r in user.roles]
    access_token = create_access_token(str(user.id), str(user.tenant_id), roles=role_cods)
    raw_refresh, refresh_hash = create_refresh_token()
    refresh = RefreshToken(
        token_hash=refresh_hash,
        user_id=user.id,
        tenant_id=user.tenant_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=raw_refresh)


@router.post("/refresh")
async def refresh(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    token_hash = hash_token(request.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    old_token = result.scalar_one_or_none()

    if old_token is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if old_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    if old_token.revoked:
        if old_token.replaced_by_token_hash:
            await db.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.user_id == old_token.user_id,
                    ~RefreshToken.revoked,
                )
                .values(revoked=True)
            )
        await db.commit()
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")

    user = await db.get(User, old_token.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    new_raw, new_hash = create_refresh_token()
    new_token = RefreshToken(
        token_hash=new_hash,
        user_id=user.id,
        tenant_id=user.tenant_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    old_token.revoked = True
    old_token.replaced_by_token_hash = new_hash

    db.add(new_token)
    await db.commit()

    role_cods = [r.codigo for r in user.roles]
    access_token = create_access_token(str(user.id), str(user.tenant_id), roles=role_cods)
    return TokenResponse(access_token=access_token, refresh_token=new_raw)


@router.post("/logout", status_code=204)
async def logout(
    request: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    token_hash = hash_token(request.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    token = result.scalar_one_or_none()

    if token is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token.revoked = True
    await db.commit()


@router.post("/2fa/enroll", response_model=TOTPEnrollResponse)
async def enroll_2fa(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.totp_enabled:
        raise HTTPException(status_code=409, detail="2FA already enabled")

    secret = pyotp.random_base32()
    current_user.totp_secret = secret
    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email,
        issuer_name="activia-trace",
    )
    await db.commit()

    return TOTPEnrollResponse(provisioning_uri=provisioning_uri, secret=secret)


@router.post("/2fa/verify")
async def verify_2fa(
    request: TOTPVerifyRequest,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
):
    if request.ephemeral_token:
        try:
            payload = decode_access_token(request.ephemeral_token)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail="Ephemeral token expired, please re-authenticate"
            )
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid ephemeral token")

        if payload.get("purpose") != "2fa":
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await db.get(User, uuid.UUID(payload["sub"]))
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        if not pyotp.TOTP(user.totp_secret).verify(request.code):
            raise HTTPException(status_code=401, detail="Invalid TOTP code")

        role_cods = [r.codigo for r in user.roles]
        access_token = create_access_token(str(user.id), str(user.tenant_id), roles=role_cods)
        raw_refresh, refresh_hash = create_refresh_token()
        refresh = RefreshToken(
            token_hash=refresh_hash,
            user_id=user.id,
            tenant_id=user.tenant_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(refresh)
        await db.commit()

        return TokenResponse(access_token=access_token, refresh_token=raw_refresh)

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    bearer_token = authorization.split(" ", 1)[1]
    try:
        payload = decode_access_token(bearer_token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.get(User, uuid.UUID(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.totp_secret:
        raise HTTPException(status_code=400, detail="No TOTP secret found. Enroll first.")

    if not pyotp.TOTP(user.totp_secret).verify(request.code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    user.totp_enabled = True
    await db.commit()

    return {"detail": "2FA enabled successfully"}


@router.post("/forgot")
async def forgot_password(
    request: ForgotRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if user is not None:
        import secrets
        raw_token = secrets.token_urlsafe(48)
        token_hash = hash_token(raw_token)
        recovery = RecoveryToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )
        db.add(recovery)
        await db.commit()

    return {"message": "If the email is registered, a recovery link has been sent"}


@router.post("/reset")
async def reset_password(
    request: ResetRequest,
    db: AsyncSession = Depends(get_db),
):
    token_hash = hash_token(request.token)
    result = await db.execute(
        select(RecoveryToken).where(RecoveryToken.token_hash == token_hash)
    )
    recovery = result.scalar_one_or_none()

    if (
        recovery is None
        or recovery.used
        or recovery.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc)
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired recovery token")

    user = await db.get(User, recovery.user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid or expired recovery token")

    recovery.used = True
    user.hashed_password = hash_password(request.new_password)
    await db.commit()

    return {"message": "Password reset successfully"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    permissions: set[str] = set()
    for rol in current_user.roles:
        for permiso in rol.permisos:
            permissions.add(permiso.codigo)
    return {
        "email": current_user.email,
        "id": str(current_user.id),
        "is_active": current_user.is_active,
        "nombre": current_user.nombre or current_user.email.split("@")[0],
        "roles": [r.codigo for r in current_user.roles],
        "permissions": sorted(permissions),
        "tenant_id": str(current_user.tenant_id),
    }
