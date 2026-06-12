## ADDED Requirements

### Requirement: AuthContext provides session state
The system SHALL provide an `AuthContext` (via `AuthProvider` at the app root) that exposes `{ user, isAuthenticated, isLoading, login(), logout(), getAccessToken() }`.

#### Scenario: AuthProvider loads user on mount from stored refresh token
- **WHEN** the app loads and a refresh token exists in localStorage
- **THEN** `isLoading` SHALL be `true` while calling `GET /api/auth/me`
- **THEN** if the call succeeds, `user` SHALL be populated with `{ id, email, roles, permissions, tenant_id }` and `isAuthenticated` SHALL be `true`
- **THEN** if the call fails (refresh token invalid/expired), `user` SHALL be `null`, `isAuthenticated` SHALL be `false`, tokens SHALL be cleared from localStorage

#### Scenario: login() authenticates and stores session
- **WHEN** `login(email, password)` is called
- **THEN** the system SHALL call `POST /api/auth/login`
- **THEN** on success, access token and refresh token SHALL be stored in memory and localStorage
- **THEN** `GET /api/auth/me` SHALL be called to populate `user`
- **THEN** `isAuthenticated` SHALL be `true`
- **THEN** if the response indicates 2FA required, a `requires2fa` flag SHALL be returned and the login flow SHALL pause pending TOTP verification

#### Scenario: logout() clears session
- **WHEN** `logout()` is called
- **THEN** the system SHALL call `POST /api/auth/logout` (best-effort, fire-and-forget)
- **THEN** tokens SHALL be cleared from memory and localStorage
- **THEN** `user` SHALL be `null`, `isAuthenticated` SHALL be `false`
- **THEN** the app SHALL redirect to `/login`

#### Scenario: getAccessToken() returns current access token
- **WHEN** `getAccessToken()` is called and a token exists
- **THEN** the system SHALL return the current access token string
- **WHEN** `getAccessToken()` is called and no token exists
- **THEN** the system SHALL return `null`

### Requirement: AuthContext holds user permissions
The system SHALL load the current user's permissions from `GET /api/auth/me` on authentication and expose them via `AuthContext.user.permissions`.

#### Scenario: Permissions are available after authentication completes
- **WHEN** login succeeds or session is restored from stored tokens
- **THEN** `user.permissions` SHALL contain the full list of permission strings resolved server-side
