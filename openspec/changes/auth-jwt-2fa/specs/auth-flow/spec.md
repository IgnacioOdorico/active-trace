## ADDED Requirements

### Requirement: User can log in with email and password
The system SHALL authenticate users via email and Argon2id-verified password. On success, it SHALL return a JWT access token (15min expiry) and a refresh token. The JWT SHALL contain `user_id`, `tenant_id`, `roles`, and `exp` claims.

#### Scenario: Successful login
- **WHEN** a user provides valid email and matching password
- **THEN** the system returns HTTP 200 with `access_token`, `refresh_token`, `token_type: "bearer"`, and the user's basic profile

#### Scenario: Login with non-existent email
- **WHEN** a user provides an email that does not exist in the system
- **THEN** the system returns HTTP 401 with a generic error message ("Invalid credentials")

#### Scenario: Login with wrong password
- **WHEN** a user provides a valid email but incorrect password
- **THEN** the system returns HTTP 401 with a generic error message ("Invalid credentials")

#### Scenario: Login with inactive user
- **WHEN** a user with `is_active = false` attempts to log in
- **THEN** the system returns HTTP 401 with "Account is inactive"

### Requirement: Refresh token rotation
The system SHALL implement refresh token rotation: using a refresh token invalidates it and issues a new pair. The old token SHALL be marked as revoked and linked to the new token via `replaced_by_token_hash`.

#### Scenario: Successful token refresh
- **WHEN** a client sends a valid, non-expired, non-revoked refresh token to `/api/auth/refresh`
- **THEN** the system returns HTTP 200 with a new `access_token` and `refresh_token`, and the old refresh token is marked as revoked

#### Scenario: Reuse of a revoked refresh token (theft detection)
- **WHEN** a client sends a refresh token that has already been used and revoked
- **THEN** the system SHALL revoke ALL refresh tokens for that user (chain invalidation) and return HTTP 401

#### Scenario: Refresh with expired token
- **WHEN** a client sends an expired refresh token
- **THEN** the system returns HTTP 401 with "Refresh token expired"

#### Scenario: Refresh with non-existent token
- **WHEN** a client sends a refresh token whose hash does not exist in the database
- **THEN** the system returns HTTP 401 with "Invalid refresh token"

### Requirement: User can log out
The system SHALL allow users to revoke their session by providing their refresh token.

#### Scenario: Successful logout
- **WHEN** an authenticated user sends a valid refresh token to `/api/auth/logout`
- **THEN** the system marks that refresh token as revoked and returns HTTP 204

### Requirement: get_current_user dependency
The system SHALL provide a FastAPI dependency that resolves the authenticated user's identity and tenant from the JWT access token.

#### Scenario: Valid access token
- **WHEN** a request includes a valid, non-expired JWT access token in the `Authorization: Bearer <token>` header
- **THEN** the dependency returns a `User` object with `id`, `email`, `tenant_id`, `roles`, `is_active`

#### Scenario: Missing or malformed token
- **WHEN** a request has no Authorization header or an invalid one
- **THEN** the dependency raises HTTP 401 with "Not authenticated"

#### Scenario: Expired access token
- **WHEN** a request includes an expired JWT access token
- **THEN** the dependency raises HTTP 401 with "Token expired"

#### Scenario: Token with invalid signature
- **WHEN** a request includes a JWT with an invalid signature
- **THEN** the dependency raises HTTP 401 with "Invalid token"
