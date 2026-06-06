## ADDED Requirements

### Requirement: Materia CRUD
The system SHALL allow tenant-scoped CRUD operations on Materia (subject) entities.

#### Scenario: Create materia
- **WHEN** an admin creates a materia with `codigo`, `nombre`, `descripcion`, and optional `carrera_id`
- **THEN** the system persists it with a generated UUID and the current tenant_id

#### Scenario: Get materia by id
- **WHEN** querying a materia by id within the same tenant
- **THEN** the system returns the materia entity

#### Scenario: List materias optionally filtered by carrera
- **WHEN** listing materias with a `carrera_id` filter
- **THEN** the system returns only materias matching that carrera within the tenant

#### Scenario: Update materia
- **WHEN** updating a materia's `nombre` or `descripcion`
- **THEN** the system updates the record and bumps `updated_at`

#### Scenario: Soft-delete materia
- **WHEN** soft-deleting a materia
- **THEN** the system sets `deleted_at` and subsequent queries exclude it

### Requirement: Materia codigo uniqueness per tenant
The system SHALL enforce that `codigo` is unique within a tenant.

#### Scenario: Duplicate codigo in same tenant rejects
- **WHEN** creating a segunda materia with the same `codigo` in the same tenant
- **THEN** the system raises an integrity error (duplicate key)

#### Scenario: Same codigo in different tenant succeeds
- **WHEN** creating a materia with the same `codigo` in a different tenant
- **THEN** the system creates it successfully (no cross-tenant collision)

### Requirement: Materia nullable carrera FK
Materia SHALL allow `carrera_id` to be null, representing cross-carrera subjects.

#### Scenario: Create materia without carrera
- **WHEN** creating a materia without providing `carrera_id`
- **THEN** the system persists it with `carrera_id` as NULL

#### Scenario: Assign carrera to materia later
- **WHEN** updating a materia to set a `carrera_id`
- **THEN** the system updates the foreign key reference
