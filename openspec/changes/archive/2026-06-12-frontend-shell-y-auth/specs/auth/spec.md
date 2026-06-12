## ADDED Requirements

### Requirement: LoginPage
The system SHALL provide a login screen at `/login` with email and password fields, form validation, and error display.

#### Scenario: LoginPage renders form fields
- **WHEN** the user navigates to `/login`
- **THEN** an email input, password input, and submit button SHALL be rendered

#### Scenario: Login validates email format
- **WHEN** the user submits with an invalid email
- **THEN** the form SHALL display a validation error for the email field
- **THEN** no API call SHALL be made

#### Scenario: Login validates password is not empty
- **WHEN** the user submits with an empty password
- **THEN** the form SHALL display a validation error for the password field
- **THEN** no API call SHALL be made

#### Scenario: Login calls POST /api/auth/login
- **WHEN** the user submits valid credentials
- **THEN** the system SHALL call `POST /api/auth/login` with the provided email and password
- **THEN** the submit button SHALL show a loading state while the request is in flight

#### Scenario: Login shows backend error
- **WHEN** the login API returns an error (invalid credentials, inactive user)
- **THEN** the form SHALL display the error message from the backend
- **THEN** the password field SHALL be cleared

#### Scenario: Login with 2FA redirects to 2FA page
- **WHEN** the login API responds with `2FA_REQUIRED`
- **THEN** the system SHALL navigate to `/login/2fa` with the ephemeral token

### Requirement: TwoFactorPage
The system SHALL provide a 2FA verification screen at `/login/2fa` for users with TOTP enabled.

#### Scenario: TwoFactorPage renders TOTP input
- **WHEN** the user is redirected to `/login/2fa`
- **THEN** a 6-digit TOTP code input and submit button SHALL be rendered

#### Scenario: TwoFactorPage validates 6-digit code
- **WHEN** the user submits a code that is not 6 digits
- **THEN** a validation error SHALL be displayed
- **THEN** no API call SHALL be made

#### Scenario: TwoFactorPage completes authentication
- **WHEN** the user submits a valid 6-digit TOTP code
- **THEN** the system SHALL call `POST /api/auth/2fa/verify` with the ephemeral token and TOTP code
- **THEN** on success, the session SHALL be established and the user SHALL be redirected to the app home

### Requirement: ForgotPasswordPage
The system SHALL provide a password recovery screen at `/forgot-password` that accepts an email and sends a recovery token.

#### Scenario: ForgotPasswordPage renders email form
- **WHEN** the user navigates to `/forgot-password`
- **THEN** an email input and submit button SHALL be rendered

#### Scenario: ForgotPasswordPage calls POST /api/auth/forgot
- **WHEN** the user submits a valid email
- **THEN** the system SHALL call `POST /api/auth/forgot` with the email
- **THEN** a success message SHALL be displayed regardless of whether the email exists in the system (to avoid user enumeration)

### Requirement: ResetPasswordPage
The system SHALL provide a password reset screen at `/reset-password` that accepts a recovery token from email and a new password.

#### Scenario: ResetPasswordPage renders new password form
- **WHEN** the user navigates to `/reset-password` with a valid token query parameter
- **THEN** new password and confirm password inputs SHALL be rendered

#### Scenario: ResetPasswordPage validates password match
- **WHEN** the user submits with mismatched passwords
- **THEN** a validation error SHALL be displayed
- **THEN** no API call SHALL be made

#### Scenario: ResetPasswordPage calls POST /api/auth/reset
- **WHEN** the user submits valid matching passwords
- **THEN** the system SHALL call `POST /api/auth/reset` with the token and new password
- **THEN** on success, the user SHALL be redirected to `/login` with a success message

### Requirement: Auth page links
The login screen SHALL provide links to the forgot password page and vice versa.

#### Scenario: Login page links to forgot password
- **WHEN** the login page is rendered
- **THEN** a "Forgot password?" link to `/forgot-password` SHALL be visible

#### Scenario: Forgot password page links to login
- **WHEN** the forgot password page is rendered
- **THEN** a "Back to login" link to `/login` SHALL be visible
