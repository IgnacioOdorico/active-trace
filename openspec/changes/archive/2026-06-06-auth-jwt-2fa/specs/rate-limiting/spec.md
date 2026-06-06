## ADDED Requirements

### Requirement: Login endpoint is rate limited by IP+email
The system SHALL limit login attempts to 5 requests per 60 seconds per unique IP+email combination. The counter SHALL reset on successful login.

#### Scenario: Under rate limit
- **WHEN** a client makes fewer than 5 login attempts for the same IP+email within 60 seconds
- **THEN** the system processes each request normally

#### Scenario: Exceeds rate limit
- **WHEN** a client makes more than 5 login attempts for the same IP+email within 60 seconds
- **THEN** the system returns HTTP 429 with `"Too many login attempts. Try again later."` and a `Retry-After` header

#### Scenario: Rate limit counter resets after window
- **WHEN** a client exceeds the rate limit and waits 60 seconds
- **THEN** the system processes the next login request normally (counter window expired)

#### Scenario: Successful login resets rate limit
- **WHEN** a client has failed 3 attempts and then succeeds on the 4th
- **THEN** the rate limit counter for that IP+email is cleared/reset

#### Scenario: Different emails for same IP have separate counters
- **WHEN** a client attempts login with 5 different emails from the same IP
- **THEN** each IP+email pair is tracked independently, each has its own 5-attempt limit

#### Scenario: Rate limit does not apply to non-login endpoints
- **WHEN** a client sends requests to `/api/auth/refresh`, `/api/auth/logout`, `/api/auth/forgot`, or `/api/auth/reset`
- **THEN** the rate limiter does not restrict these requests
