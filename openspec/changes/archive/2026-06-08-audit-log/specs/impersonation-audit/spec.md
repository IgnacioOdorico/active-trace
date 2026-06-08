## ADDED Requirements

### Requirement: Impersonacion:usar permission

The system SHALL add the `impersonacion:usar` permission to the seed data for the ADMIN role.
The ADMIN role SHALL be seeded with `impersonacion:usar`.
The permission description SHALL be "Usar impersonación".
No other roles SHALL have `impersonacion:usar` by default.

#### Scenario: ADMIN has impersonacion:usar
- **WHEN** the seed runs or migration 003 updates
- **THEN** the ADMIN role has the `impersonacion:usar` permission

#### Scenario: Non-ADMIN roles lack impersonacion:usar
- **WHEN** checking any non-ADMIN role
- **THEN** `impersonacion:usar` is not in their permission set

### Requirement: Impersonation session tracking

The system SHALL track impersonation state in the current session/request context.
The session SHALL be distinguishable from a normal session:
- The JWT payload SHALL include an `impersonating` claim (boolean, default `false`)
- When impersonating, the JWT SHALL also include:
  - `impersonator_id`: the original actor's user ID
  - `impersonated_user_id`: the target user's ID
  - `original_roles`: the impersonator's original role IDs

The `get_current_user` dependency SHALL expose the impersonation context, so that downstream code can determine:
- Who the real actor is (`impersonator_id`)
- Who is being impersonated (`impersonated_user_id`)

#### Scenario: Normal session JWT
- **WHEN** a user logs in normally
- **THEN** the JWT has `impersonating: false`
- **AND** no impersonation fields are present

#### Scenario: Impersonation session JWT
- **WHEN** an ADMIN starts impersonating another user
- **THEN** the JWT has `impersonating: true`
- **AND** includes `impersonator_id` and `impersonated_user_id`

### Requirement: IMPERSONACION_INICIAR / IMPERSONACION_FINALIZAR audit events

The system SHALL register `IMPERSONACION_INICIAR` when an impersonation session starts.
The system SHALL register `IMPERSONACION_FINALIZAR` when an impersonation session ends.

Both events SHALL record:
- `actor_id`: the impersonator (real user)
- `impersonado_id`: the user being impersonated
- `detalle`: includes both user identifiers

#### Scenario: Start impersonation creates audit entry
- **WHEN** an ADMIN starts impersonating a user
- **THEN** an audit entry with `accion = "IMPERSONACION_INICIAR"` is created
- **AND** `actor_id` is the impersonator
- **AND** `impersonado_id` is the impersonated user

#### Scenario: End impersonation creates audit entry
- **WHEN** an ADMIN stops impersonating a user
- **THEN** an audit entry with `accion = "IMPERSONACION_FINALIZAR"` is created

### Requirement: Actions during impersonation attributed to real actor

Every action performed during an impersonation session SHALL be logged with:
- `actor_id`: the impersonator (real user who performed the action)
- `impersonado_id`: the user being impersonated (the "mask" user)

The `impersonado_id` field in the audit entry SHALL be populated when `impersonating = true` in the current session.

#### Scenario: Action logged during impersonation
- **WHEN** a user performs an action while impersonating another user
- **THEN** the audit entry has `actor_id` = impersonator's ID
- **AND** `impersonado_id` = impersonated user's ID
