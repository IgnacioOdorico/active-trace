## ADDED Requirements

### Requirement: User can enroll in TOTP 2FA
The system SHALL allow an authenticated user to generate a TOTP secret and receive a provisioning URI (for QR code generation).

#### Scenario: Enroll in 2FA
- **WHEN** an authenticated user without active 2FA calls `POST /api/auth/2fa/enroll`
- **THEN** the system generates a new TOTP secret, stores it temporarily (or permanently as unverified), and returns `provisioning_uri`, `secret` (base32), and a QR code as a data URL or raw string

### Requirement: User can verify and enable TOTP 2FA
The system SHALL allow the user to verify a TOTP code to confirm the setup and enable 2FA on their account.

#### Scenario: Successful 2FA verification
- **WHEN** a user provides a valid TOTP code matching their stored secret via `POST /api/auth/2fa/verify`
- **THEN** the system sets `totp_enabled = true` for the user and returns HTTP 200

#### Scenario: Invalid TOTP code
- **WHEN** a user provides an invalid TOTP code
- **THEN** the system returns HTTP 400 with "Invalid TOTP code"

#### Scenario: 2FA already enabled
- **WHEN** a user with `totp_enabled = true` calls enroll
- **THEN** the system returns HTTP 409 with "2FA already enabled"

### Requirement: Login with 2FA requires TOTP code
The system SHALL gate the login flow when the user has 2FA enabled. After credential validation, the system issues a short-lived ephemeral token that is exchanged for the session pair only after TOTP verification.

#### Scenario: Login with 2FA — first step credentials
- **WHEN** a user with `totp_enabled = true` provides valid email and password
- **THEN** the system returns HTTP 200 with `status: "2FA_REQUIRED"` and an `ephemeral_token` (5min expiry)

#### Scenario: Login with 2FA — complete with TOTP
- **WHEN** a user provides a valid ephemeral token and a valid TOTP code
- **THEN** the system returns HTTP 200 with `access_token`, `refresh_token`, `token_type: "bearer"`

#### Scenario: Login with 2FA — invalid TOTP
- **WHEN** a user provides a valid ephemeral token but invalid TOTP code
- **THEN** the system returns HTTP 401 with "Invalid TOTP code"

#### Scenario: Login with 2FA — expired ephemeral token
- **WHEN** a user provides an expired ephemeral token and any TOTP code
- **THEN** the system returns HTTP 401 with "Ephemeral token expired, please re-authenticate"
