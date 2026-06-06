## Why

Authentication is the next critical piece after tenancy. Without it the system cannot issue sessions, enforce identity, or protect resources. C-02 established Tenant isolation and the repository pattern; this change builds the identity layer on top: login, session management with refresh rotation, optional 2FA TOTP, password recovery, and rate limiting.

## What Changes

- **User model** (`users` table) with email, Argon2id-hashed password, TOTP secret, foreign key to Tenant
- **RefreshToken model** (`refresh_tokens` table) with token hash, FK to User+Tenant, expiration, revoke flag, and `replaced_by_token_hash` for rotation tracking
- `POST /api/auth/login` — email + password validation, optional 2FA TOTP gate, JWT access token (15min) + refresh token pair
- `POST /api/auth/refresh` — rotates refresh token (old one invalidated), emits new pair
- `POST /api/auth/logout` — revokes session (marks refresh token as revoked)
- `POST /api/auth/2fa/enroll` — generates TOTP secret, returns provisioning URI + QR
- `POST /api/auth/2fa/verify` — confirms TOTP setup, enables 2FA for user
- `POST /api/auth/forgot` — single-use recovery token sent by email, short expiry
- `POST /api/auth/reset` — validates recovery token, sets new password
- Rate limiting 5 requests per 60s per IP+email on login endpoint
- `get_current_user` dependency that resolves identity + tenant from verified JWT
- Alembic migration for new tables

## Capabilities

### New Capabilities
- `auth-flow`: Login with Argon2id, JWT access+refresh pair with rotation, logout, get_current_user dependency
- `fa-totp`: Optional TOTP 2FA per user — enroll, verify, gate between credential validation and session issuance
- `password-recovery`: Forgot/reset flow with single-use token, short expiry
- `rate-limiting`: 5 requests per 60s per IP+email on login

### Modified Capabilities
<!-- No existing capabilities are modified — this is the first identity layer -->

## Impact

- **New models**: `User` (app/models/user.py), `RefreshToken` (app/models/refresh_token.py)
- **New service**: `AuthService` (app/services/auth.py) — password hashing, JWT creation/verification, refresh rotation, 2FA
- **New router**: `app/api/v1/routers/auth.py` with all auth endpoints
- **New dependency**: `get_current_user` in `app/core/dependencies.py`
- **New dependency**: `pyotp` for TOTP, `itsdangerous` or similar for recovery tokens
- **New migration**: `002_users_refresh_tokens`
- **Rate limiter**: simple in-memory dict or a dedicated `app/core/rate_limiter.py`
- **Tests**: `tests/test_auth.py`, `tests/test_2fa.py`, `tests/test_rate_limit.py`
