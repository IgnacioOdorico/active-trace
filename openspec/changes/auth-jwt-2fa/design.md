## Context

C-02 established the multi-tenant foundation: Tenant model, EntityMeta mixin, BaseRepository with tenant scope, AES-256 encryption, and DomainError exceptions. The identity layer is the next critical piece — the system cannot protect resources or issue sessions without it.

The current codebase has an empty `tenancy.py`, a placeholder in `dependencies.py` for `get_current_user`, and Argon2id + python-jose already declared in `pyproject.toml`. All wired components (Settings, database session, Base) follow the patterns established in C-02.

## Goals / Non-Goals

**Goals:**
- Email + password authentication using Argon2id
- JWT access tokens (15min) with minimal claims: `user_id`, `tenant_id`, `roles`, `exp`
- Refresh token rotation: each refresh invalidates the previous token (rotation chain)
- Optional TOTP 2FA gated between credential validation and session issuance
- Password recovery with single-use token, short expiry, emailed to user
- Rate limiting: 5 requests per 60s per IP+email on login
- `get_current_user` dependency resolving identity + tenant from verified JWT
- Logout revokes the refresh token
- Full test coverage per CHANGES.md specification

**Non-Goals:**
- RBAC permission checks (C-04)
- Audit logging of auth events (C-05)
- OAuth2 / social login
- Session persistence beyond refresh token table
- Email delivery infrastructure (async worker — deferred to future change)
- Rate limiting on non-login endpoints (deferred)

## Decisions

1. **Refresh token rotation model**: The refresh token table tracks a chain via `replaced_by_token_hash`. When a refresh token is used, its `revoked` flag is set to true and the new token's hash is stored in `replaced_by_token_hash`. If a revoked token is reused (theft detection), the ENTIRE chain is invalidated — all tokens for that user are revoked. This follows the IETF OAuth 2.0 rotation best practice.

2. **Token storage**: Only the SHA-256 hash of the refresh token is stored in the database. The raw token (a `secrets.token_urlsafe(48)` string) is returned to the client and never persisted. This means a DB leak does not expose active refresh tokens.

3. **2FA as optional gate**: TOTP is per-user optional. If `totp_enabled` is true for the user, login returns a `2FA_REQUIRED` status with a temporary ephemeral token. The client must then call `/api/auth/2fa/verify` with the TOTP code + ephemeral token to complete login. This avoids exposing the JWT pair before 2FA is satisfied.

4. **Ephemeral token**: A short-lived (5min) JWT signed with a separate rotation key, containing only `user_id`, `tenant_id`, and `purpose=2fa`. Issued only after credential validation passes but before 2FA gate. Not stored in DB.

5. **Rate limiting strategy**: In-memory dict with IP+email as composite key, sliding window via sorted list of timestamps. Not production-grade but sufficient for current phase. Cleanup on login success. Designed as a replaceable module (`app/core/rate_limiter.py`) so a Redis-backed implementation can swap in later.

6. **Password recovery tokens**: Short-lived (15min) single-use token stored as SHA-256 hash in a new field or table. The raw token is emailed. No session issuance on reset — user must log in with the new password.

7. **JWT signing**: HMAC-SHA256 using `python-jose` with the `SECRET_KEY` from Settings. Access token expiry: 15 minutes. Refresh token expiry: 7 days (not in JWT — validated against DB `expires_at`).

8. **Identity immutability**: `get_current_user` reads `user_id` and `tenant_id` from JWT claims only. No request parameter can override these. The user's roles are also read from the JWT — these are populated at login and refreshed on token rotation.

## Risks / Trade-offs

- **[Risk] In-memory rate limiter resets on app restart** → Acceptable for initial release. The limiter is specifically for login brute-force protection; a restart clears counters, which is better than a stuck counter. Documented as tech debt toward Redis.
- **[Risk] Recovery tokens emailed in plain text** → The token is single-use and short-lived (15min). The email itself is a risk vector if intercepted. Mitigation: the reset endpoint invalidates the token on first use regardless of success. Full mitigation requires TLS and is noted.
- **[Risk] Refresh token rotation theft detection** → If an attacker steals a refresh token and both attacker and victim use it, the victim's legitimate use triggers invalidation of the entire chain — locking out both. Mitigation: the user can re-authenticate. This is a deliberate trade-off: security over UX in the theft scenario.
- **[Trade-off] No async email worker** → Recovery emails are synchronous. For MVP this is acceptable. Future C-12 worker will handle async email dispatch.
