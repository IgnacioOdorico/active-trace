## ADDED Requirements

### Requirement: AuditLog entity (append-only)

The system SHALL provide an `AuditLog` model stored in the `audit_log` table.
The model SHALL NOT inherit from `EntityMeta` — it uses a simplified base with ONLY:
- `id: UUID` (PK, default uuid4)
- `tenant_id: UUID` (FK → tenant, NOT NULL)
- `fecha_hora: DateTime` (timezone-aware, server_default=func.now(), NOT NULL)
- `actor_id: UUID` (FK → users, NOT NULL)
- `impersonado_id: UUID` (FK → users, NULLABLE)
- `materia_id: UUID` (FK → materias, NULLABLE)
- `accion: String(100)` (NOT NULL)
- `detalle: JSON` (nullable)
- `filas_afectadas: Integer` (default 0)
- `ip: String(45)` (nullable)
- `user_agent: String(500)` (nullable)

The model SHALL be **append-only**:
- NO update operation allowed at the application level
- NO delete operation allowed at the application level
- NO soft-delete (`deleted_at`) — the record is immutable
- `AuditLog` SHALL have NO `updated_at` column
- `AuditLog` SHALL have NO `deleted_at` column

The repository layer for AuditLog SHALL expose only `create()` and `list()` methods — no `update()`, `delete()`, or `soft_delete()`.

#### Scenario: Create audit log entry
- **WHEN** a new audit log entry is created
- **THEN** the entry has `id`, `tenant_id`, `fecha_hora`, `actor_id`, `accion`, and optionally `impersonado_id`, `materia_id`, `detalle`, `filas_afectadas`, `ip`, `user_agent`
- **AND** `fecha_hora` defaults to the current timestamp
- **AND** `filas_afectadas` defaults to 0

#### Scenario: No update allowed
- **WHEN** code attempts to update an existing AuditLog entry
- **THEN** the system SHALL raise an error (not supported)

#### Scenario: No delete allowed
- **WHEN** code attempts to delete or soft-delete an AuditLog entry
- **THEN** the system SHALL raise an error (not supported)

#### Scenario: AuditLog tenant-isolated
- **WHEN** querying audit log entries
- **THEN** results SHALL be filtered to the current `tenant_id`

### Requirement: Action codes catalog

The system SHALL use standardized action codes in format `MODULO_ACCION` (e.g., `CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`).
The following codes SHALL be defined as constants in the service layer:
- `CALIFICACIONES_IMPORTAR`
- `PADRON_CARGAR`
- `COMUNICACION_ENVIAR`
- `ASIGNACION_MODIFICAR`
- `LIQUIDACION_CERRAR`
- `IMPERSONACION_INICIAR`
- `IMPERSONACION_FINALIZAR`

#### Scenario: Action code used when logging
- **WHEN** an audit entry is created
- **THEN** the `accion` field SHALL contain one of the standardized codes

### Requirement: AuditLog Pydantic schemas

The system SHALL provide Pydantic v2 schemas:
- `AuditLogResponse`: `id` (str), `fecha_hora`, `actor_id` (str), `impersonado_id` (str | None), `materia_id` (str | None), `accion`, `detalle` (dict | None), `filas_afectadas`, `ip` (str | None), `user_agent` (str | None)
- `AuditLogFilter`: optional filters for `actor_id`, `materia_id`, `accion`, `desde`, `hasta`, `pagina`, `por_pagina`

There SHALL be NO `AuditLogCreate` or `AuditLogUpdate` schema — creation is internal via the service layer only.

#### Scenario: Response schema exposes all fields
- **WHEN** an AuditLog entry is serialized to response
- **THEN** all fields are present with `id`, `actor_id`, `materia_id`, `impersonado_id` as strings (not UUIDs)

### Requirement: Migration 005

The Alembic migration `005_create_audit_log.py` SHALL:
- Depend on revision `004`
- Create the `audit_log` table with all columns
- Create FK constraints for `tenant_id`, `actor_id`, `impersonado_id`, `materia_id`
- Create an index on `(tenant_id, accion)` for filtered lookups
- Create an index on `(tenant_id, actor_id)` for per-user queries
- Create an index on `(tenant_id, fecha_hora)` for time-range queries

#### Scenario: Migration creates audit_log table
- **WHEN** migration 005 is applied
- **THEN** the `audit_log` table exists with all columns and constraints
