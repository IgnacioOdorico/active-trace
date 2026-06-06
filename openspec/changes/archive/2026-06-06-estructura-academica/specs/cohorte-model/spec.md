## ADDED Requirements

### Requirement: Cohorte CRUD
The system SHALL allow tenant-scoped CRUD operations on Cohorte (cohort) entities.

#### Scenario: Create cohorte
- **WHEN** an admin creates a cohorte with `nombre`, `carrera_id`, `fecha_inicio`, `fecha_fin`
- **THEN** the system persists it with a generated UUID, the current tenant_id, and `activa` defaulting to True

#### Scenario: Get cohorte by id
- **WHEN** querying a cohorte by id within the same tenant
- **THEN** the system returns the cohorte entity

#### Scenario: List cohortes filtered by carrera
- **WHEN** listing cohortes with a `carrera_id` filter
- **THEN** the system returns only cohortes matching that carrera within the tenant

#### Scenario: Update cohorte
- **WHEN** updating a cohorte's `nombre` or dates
- **THEN** the system updates the record and bumps `updated_at`

#### Scenario: Soft-delete cohorte
- **WHEN** soft-deleting a cohorte
- **THEN** the system sets `deleted_at` and subsequent queries exclude it

### Requirement: Cohorte nombre uniqueness per tenant and carrera
The system SHALL enforce that `nombre` is unique within the combination of `tenant_id` and `carrera_id`.

#### Scenario: Duplicate nombre in same tenant and carrera rejects
- **WHEN** creating a cohorte with the same `nombre` and `carrera_id` in the same tenant
- **THEN** the system raises an integrity error (duplicate key)

#### Scenario: Same nombre in different carrera within same tenant succeeds
- **WHEN** creating a cohorte with the same `nombre` but different `carrera_id` within the same tenant
- **THEN** the system creates it successfully

### Requirement: Cohorte active state tied to carrera
The system SHALL enforce that cohortes can only be active when their referenced carrera is active.

#### Scenario: Create cohorte on inactive carrera is rejected
- **WHEN** attempting to create a cohorte referencing an inactive carrera
- **THEN** the system raises a business rule error

#### Scenario: Activate cohorte on re-activated carrera
- **WHEN** a carrera is reactivated
- **THEN** its cohortes can be activated again
