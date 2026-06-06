## ADDED Requirements

### Requirement: User can request password recovery
The system SHALL allow a user to request a password reset by providing their registered email. A single-use recovery token SHALL be generated and made available (for now, returned in the response; future: sent via email worker).

#### Scenario: Forgot password with registered email
- **WHEN** an unauthenticated user provides a registered email to `POST /api/auth/forgot`
- **THEN** the system generates a single-use recovery token (48 bytes, URL-safe), stores its SHA-256 hash with a 15-minute expiry, and returns `message: "If the email is registered, a recovery link has been sent"`

#### Scenario: Forgot password with unregistered email
- **WHEN** an unauthenticated user provides an unregistered email to `POST /api/auth/forgot`
- **THEN** the system returns the same generic message: `"If the email is registered, a recovery link has been sent"` (to prevent email enumeration)

### Requirement: User can reset password with recovery token
The system SHALL allow a user to set a new password using a valid, non-expired, non-revoked recovery token.

#### Scenario: Successful password reset
- **WHEN** a user provides a valid recovery token and a new password (min 8 characters) to `POST /api/auth/reset`
- **THEN** the system invalidates the recovery token, hashes the new password with Argon2id, updates the user's password, and returns HTTP 200

#### Scenario: Reset with invalid token
- **WHEN** a user provides a recovery token whose hash does not exist in the database
- **THEN** the system returns HTTP 400 with "Invalid or expired recovery token"

#### Scenario: Reset with expired token
- **WHEN** a user provides a recovery token that has exceeded its 15-minute expiry
- **THEN** the system returns HTTP 400 with "Invalid or expired recovery token"

#### Scenario: Reset with reused token
- **WHEN** a user provides a recovery token that has already been used
- **THEN** the system returns HTTP 400 with "Invalid or expired recovery token"

#### Scenario: Reset with weak password
- **WHEN** a user provides a valid recovery token but a password shorter than 8 characters
- **THEN** the system returns HTTP 422 with validation error for password length
