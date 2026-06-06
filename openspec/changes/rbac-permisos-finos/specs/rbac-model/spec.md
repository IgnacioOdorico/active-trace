## ADDED Requirements

### Requirement: Rol entity
The system SHALL define a Rol model with UUID primary key, unique `codigo` (e.g., `ALUMNO`, `TUTOR`, `PROFESOR`), `nombre` (human-readable), `descripcion`, `activo` boolean, and `entity_meta` (timestamps via EntityMeta mixin).

#### Scenario: Create rol with valid codigo
- **WHEN** creating a Rol with codigo `"COORDINADOR"`
- **THEN** the entity SHALL be persisted with a UUID, activo=True, and auto-generated timestamps

#### Scenario: Duplicate codigo is rejected
- **WHEN** attempting to create a Rol with a codigo that already exists
- **THEN** the system SHALL raise an integrity error

### Requirement: Permiso entity
The system SHALL define a Permiso model with UUID primary key, unique `codigo` in `"modulo:accion"` format (e.g., `"equipos:asignar"`, `"liquidaciones:*"`), `nombre`, `descripcion`, `propio` boolean (default False), and EntityMeta mixin.

#### Scenario: Create permiso with valid codigo
- **WHEN** creating a Permiso with codigo `"equipos:asignar"`
- **THEN** the entity SHALL be persisted with propio=False and auto-generated timestamps

#### Scenario: Propio-scoped permission
- **WHEN** creating a Permiso with codigo `"atrasados:ver"` and propio=True
- **THEN** propio SHALL be persisted as True

### Requirement: RolPermiso association
The system SHALL define a RolPermiso association model linking Rol and Permiso via foreign keys, with an `ambito` field (nullable string, e.g., `"propio"`, `"global"`). A rol can have many permisos, a permiso can belong to many roles (M:N).

#### Scenario: Assign permission to role
- **WHEN** creating a RolPermiso linking Rol `"ADMIN"` and Permiso `"liquidaciones:*"`
- **THEN** the association SHALL be persisted and queryable from both sides

#### Scenario: Cascade delete behavior
- **WHEN** a Rol is deleted
- **THEN** its RolPermiso associations SHALL be cascade-deleted

### Requirement: Seed 7 canonical roles
The system SHALL seed the following roles at migration time: ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS — each with their full permission matrix as defined in 03_actores_y_roles.md §3.3.

#### Scenario: All 7 roles exist after migration
- **WHEN** migration 003 runs
- **THEN** the rol table SHALL contain exactly 7 rows with the canonical codigos
- **AND** each role SHALL have its corresponding permisos via RolPermiso

### Requirement: Permiso catalog seed
The system SHALL seed all permissions referenced by the 7 canonical roles at migration time. Permissions are defined as `modulo:accion` pairs.

#### Scenario: Permisos exist after migration
- **WHEN** migration 003 runs
- **THEN** all permisos referenced by any seeded role SHALL exist in the permiso table
