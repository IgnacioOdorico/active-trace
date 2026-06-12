## ADDED Requirements

### Requirement: Centralized HTTP client
The system SHALL provide a single Axios instance (`apiClient`) configured with the API base URL, default headers, and auth interceptors.

#### Scenario: Request interceptor attaches JWT Bearer token
- **WHEN** any request is made through `apiClient` and a valid access token exists in AuthContext
- **THEN** the request SHALL include an `Authorization: Bearer <token>` header

#### Scenario: Request interceptor omits token when no session exists
- **WHEN** any request is made through `apiClient` and no access token exists (anonymous request)
- **THEN** the request SHALL NOT include an Authorization header

#### Scenario: Response interceptor catches 401 and attempts transparent refresh
- **WHEN** a request receives a 401 response
- **THEN** the interceptor SHALL attempt to call `POST /api/auth/refresh` with the stored refresh token
- **THEN** if refresh succeeds, the interceptor SHALL update the stored tokens and retry the original request with the new access token
- **THEN** if refresh fails, the interceptor SHALL clear the session and redirect to `/login`

#### Scenario: Concurrent 401s share a single refresh
- **WHEN** multiple requests receive 401 responses simultaneously
- **THEN** only one refresh call SHALL be in flight at a time
- **THEN** all queued requests SHALL retry with the new token once refresh completes

#### Scenario: Logout clears session before 401 handling
- **WHEN** `logout()` is called
- **THEN** the interceptor SHALL NOT attempt transparent refresh on subsequent 401s
- **THEN** the interceptor SHALL redirect to `/login` instead
