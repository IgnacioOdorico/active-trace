## ADDED Requirements

### Requirement: require_permission FastAPI dependency
The system SHALL provide a `require_permission(codigo: str)` callable that returns a FastAPI dependency. When invoked, it SHALL:
- Extract user role IDs from the JWT `rols` claim
- Query RolPermiso for any matching permission row where the role is one of the user's roles AND the permiso matches `codigo`
- Return 403 if no matching row is found

#### Scenario: User has the required permission
- **WHEN** a request is made to an endpoint protected with `require_permission("equipos:asignar")`
- **AND** the authenticated user has a role linked to that permission
- **THEN** the request SHALL proceed to the handler

#### Scenario: User lacks the required permission
- **WHEN** a request is made to an endpoint protected with `require_permission("equipos:asignar")`
- **AND** the authenticated user has no role linked to that permission
- **THEN** the system SHALL return 403 Forbidden

#### Scenario: Anonymous user blocked
- **WHEN** an unauthenticated request reaches an endpoint protected with require_permission
- **THEN** the system SHALL return 401 Unauthorized (via get_current_user)

### Requirement: Wildcard permission matching
The system SHALL support `*` wildcard in both modulo and accion positions. `"liquidaciones:*"` matches any action in liquidaciones.

#### Scenario: Wildcard action matches all actions
- **WHEN** a Rol has Permiso `"liquidaciones:*"`
- **AND** a user with that role accesses `require_permission("liquidaciones:ver")`
- **THEN** the request SHALL proceed

#### Scenario: Wildcard module matches all modules
- **WHEN** a Rol has Permiso `"*:ver"`
- **THEN** any `require_permission("<modulo>:ver")` check SHALL pass for that role

### Requirement: (propio) scope checking
The system SHALL allow `require_permission` to accept an optional `own_resource_check` parameter. When the matching Permiso has `propio=True`, the guard SHALL invoke the callable; if it returns False, return 403.

#### Scenario: Propio check passes
- **WHEN** a request requires `"atrasados:ver"` (propio=True)
- **AND** the own_resource_check callable returns True
- **THEN** the request SHALL proceed

#### Scenario: Propio check fails
- **WHEN** a request requires `"atrasados:ver"` (propio=True)
- **AND** the own_resource_check callable returns False
- **THEN** the system SHALL return 403 Forbidden

### Requirement: JWT rols claim
The system SHALL include a `"rols"` claim in the JWT payload containing a list of role UUID strings. `create_access_token` SHALL accept an optional `roles: list[str]` parameter.

#### Scenario: Token contains roles
- **WHEN** creating a token with roles=["role-uuid-1", "role-uuid-2"]
- **THEN** the decoded JWT payload SHALL contain `"rols": ["role-uuid-1", "role-uuid-2"]`

#### Scenario: Token without roles
- **WHEN** creating a token without specifying roles
- **THEN** the JWT payload SHALL contain `"rols": []`
