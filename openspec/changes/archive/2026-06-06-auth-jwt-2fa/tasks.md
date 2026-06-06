## 1. Models and Database

- [x] 1.1 Create `User` model with email, hashed_password, is_active, totp_secret (nullable String), totp_enabled (default False), foreign key to Tenant
- [x] 1.2 Create `RefreshToken` model with token_hash, user_id FK, tenant_id FK, expires_at, revoked (default False), replaced_by_token_hash (nullable)
- [x] 1.3 Create `RecoveryToken` model with token_hash, user_id FK, expires_at, used (default False)
- [x] 1.4 Create Alembic migration `002_users_refresh_tokens` for User, RefreshToken, and RecoveryToken tables
- [x] 1.5 Register new models in `app/models/__init__.py`

## 2. Auth Service — Password and JWT Core

- [x] 2.1 Implement `hash_password(password) -> str` using Argon2id
- [x] 2.2 Implement `verify_password(password, hashed) -> bool` using Argon2id
- [x] 2.3 Implement `create_access_token(user) -> str` with claims: user_id, tenant_id, roles, exp (15min)
- [x] 2.4 Implement `decode_access_token(token) -> dict` that validates signature and expiry, returns payload
- [x] 2.5 Implement `create_refresh_token() -> tuple[str, str]` returning (raw_token, sha256_hash)
- [x] 2.6 Implement `create_ephemeral_token(user) -> str` for 2FA flow (5min, purpose=2fa)
- [x] 2.7 Implement `hash_token(raw) -> str` utility (SHA-256 hexdigest)

## 3. Auth Endpoints — Login, Refresh, Logout

- [x] 3.1 Create `POST /api/auth/login` — validates email+password, checks user active, returns JWT pair (or 2FA_REQUIRED if totp_enabled)
- [x] 3.2 Create `POST /api/auth/refresh` — validates refresh token hash, rotates (revoke old + issue new pair), chain invalidation on reuse detection
- [x] 3.3 Create `POST /api/auth/logout` — validates refresh token hash, marks revoked
- [x] 3.4 Register auth router in FastAPI app

## 4. Rate Limiting

- [x] 4.1 Implement `RateLimiter` class in `app/core/rate_limiter.py` — in-memory dict with composite key IP+email, sliding window, 5/60s
- [x] 4.2 Wire rate limiter as a dependency or decorator on the login endpoint
- [x] 4.3 Clear rate limit counter on successful login

## 5. 2FA TOTP

- [x] 5.1 Create `POST /api/auth/2fa/enroll` — generates TOTP secret, returns provisioning URI + secret (requires authenticated user)
- [x] 5.2 Create `POST /api/auth/2fa/verify` — validates TOTP code + ephemeral token, completes login, returns JWT pair; or validates TOTP code for enrollment confirmation (enables totp_enabled)
- [x] 5.3 Wire ephemeral token verification into login flow (gate between credentials and session issuance)

## 6. Password Recovery

- [x] 6.1 Create `POST /api/auth/forgot` — generates recovery token (48 bytes URL-safe), stores hash with 15min expiry, returns generic success message
- [x] 6.2 Create `POST /api/auth/reset` — validates recovery token hash, checks expiry/used, hashes new password, updates user, marks token used

## 7. Dependencies

- [x] 7.1 Implement `get_current_user` FastAPI dependency in `app/core/dependencies.py` — extracts Bearer token, decodes JWT, fetches User from DB, returns user
- [x] 7.2 Implement `get_tenant` FastAPI dependency in `app/core/dependencies.py` — resolves tenant from JWT claims (tenant_id)

## 8. Tests

- [x] 8.1 Write tests for User and RefreshToken models (creation, relationships, constraints)
- [x] 8.2 Write tests for password hashing (hash + verify round-trip, wrong password rejects)
- [x] 8.3 Write tests for JWT creation and decoding (valid token, expired, invalid signature)
- [x] 8.4 Write tests for login endpoint (success, wrong password, inactive user, non-existent email)
- [x] 8.5 Write tests for refresh token rotation (successful refresh, reuse revoked token triggers chain invalidation, expired token)
- [x] 8.6 Write tests for logout (revokes refresh token)
- [x] 8.7 Write tests for 2FA TOTP (enroll, verify, login with 2FA gate, invalid TOTP code)
- [x] 8.8 Write tests for password recovery (forgot, reset success, invalid token, expired token, reused token)
- [x] 8.9 Write tests for rate limiting (under limit passes, exceeds returns 429, counter reset on success, separate IP+email counters)
- [x] 8.10 Write tests for get_current_user (valid token, missing header, expired token, invalid signature)

## 9. Final Verification

- [x] 9.1 Run full test suite — all auth tests pass (126 passed, 39 skipped due to no PostgreSQL)
- [x] 9.2 Run linting (ruff check) on all new and modified files
- [x] 9.3 Verify app routes — all 7 auth endpoints registered correctly
- [x] 9.4 Verify auth service — password hashing, JWT create/decode, refresh tokens all verified
