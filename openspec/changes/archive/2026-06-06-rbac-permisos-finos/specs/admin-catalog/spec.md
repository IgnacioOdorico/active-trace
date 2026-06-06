## ADDED Requirements

### Requirement: Admin-only role management
The system SHALL provide CRUD endpoints for managing roles at `/api/v1/admin/roles`. All endpoints SHALL require `require_permission("admin:roles")`.

#### Scenario: List all roles
- **WHEN** an admin GETs `/api/v1/admin/roles`
- **THEN** the system SHALL return a paginated list of all roles

#### Scenario: Create a new role
- **WHEN** an admin POSTs to `/api/v1/admin/roles` with a valid body `{codigo, nombre, descripcion}`
- **THEN** the system SHALL create and return the new role

#### Scenario: Update a role
- **WHEN** an admin PUTs to `/api/v1/admin/roles/{rol_id}` with updated fields
- **THEN** the system SHALL update and return the role

#### Scenario: Delete a role (soft)
- **WHEN** an admin DELETEs `/api/v1/admin/roles/{rol_id}`
- **THEN** the system SHALL set activo=False on the role

#### Scenario: Non-admin gets 403
- **WHEN** a non-admin user accesses `/api/v1/admin/roles`
- **THEN** the system SHALL return 403 Forbidden

### Requirement: Admin-only permission management
The system SHALL provide CRUD endpoints for managing permissions at `/api/v1/admin/permisos`. All endpoints SHALL require `require_permission("admin:permisos")`.

#### Scenario: List all permissions
- **WHEN** an admin GETs `/api/v1/admin/permisos`
- **THEN** the system SHALL return a paginated list of all permissions

#### Scenario: Create a new permission
- **WHEN** an admin POSTs to `/api/v1/admin/permisos` with a valid body `{codigo, nombre, descripcion, propio}`
- **THEN** the system SHALL create and return the new permission

### Requirement: Admin-only role-permission assignment
The system SHALL provide endpoints for managing RolPermiso assignments at `/api/v1/admin/roles/{rol_id}/permisos`. All endpoints SHALL require `require_permission("admin:roles")`.

#### Scenario: Assign permission to role
- **WHEN** an admin POSTs to `/api/v1/admin/roles/{rol_id}/permisos` with `{permiso_id}`
- **THEN** the system SHALL add the permission to the role and return the association

#### Scenario: Remove permission from role
- **WHEN** an admin DELETEs `/api/v1/admin/roles/{rol_id}/permisos/{permiso_id}`
- **THEN** the system SHALL remove the permission from the role
