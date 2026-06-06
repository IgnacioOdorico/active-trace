## ADDED Requirements

### Requirement: Carrera CRUD
The system SHALL allow tenant-scoped CRUD operations on Carrera (degree program) entities.

#### Scenario: Create carrera
- **WHEN** an admin creates a carrera with `codigo`, `nombre`, `descripcion`
- **THEN** the system persists it with a generated UUID, the current tenant_id, and `activa` defaulting to True

#### Scenario: Get carrera by id
- **WHEN** querying a carrera by id within the same tenant
- **THEN** the system returns the carrera entity

#### Scenario: Get carrera from different tenant returns None
- **WHEN** querying a carrera by id from a different tenant
- **THEN** the system returns None (tenant isolation)

#### Scenario: List carreras
- **WHEN** listing carreras for a tenant
- **THEN** the system returns only non-deleted carreras scoped to that tenant

#### Scenario: Update carrera
- **WHEN** updating a carrera's `nombre` or `descripcion`
- **THEN** the system updates the record and bumps `updated_at`

#### Scenario: Soft-delete carrera
- **WHEN** soft-deleting a carrera
- **THEN** the system sets `deleted_at` and subsequent queries exclude it

### Requirement: Carrera codigo uniqueness per tenant
The system SHALL enforce that `codigo` is unique within a tenant.

#### Scenario: Create duplicate codigo in same tenant rejects
- **WHEN** creating a segunda carrera with the same `codigo` in the same tenant
- **THEN** the system raises an integrity error (duplicate key)

#### Scenario: Same codigo in different tenant succeeds
- **WHEN** creating a carrera with the same `codigo` in a different tenant
- **THEN** the system creates it successfully (no cross-tenant collision)

### Requirement: Carrera active/inactive state
The system SHALL support activating and deactivating a carrera.

#### Scenario: Deactivate carrera with no active cohorts succeeds
- **WHEN** deactivating a carrera that has no active cohorts
- **THEN** the system sets `activa` to False

#### Scenario: Deactivate carrera with active cohorts is rejected
- **WHEN** attempting to deactivate a carrera that has active cohorts
- **THEN** the system raises a business rule error and does NOT deactivate
