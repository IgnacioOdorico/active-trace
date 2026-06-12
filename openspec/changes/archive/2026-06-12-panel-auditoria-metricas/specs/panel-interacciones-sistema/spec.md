## ADDED Requirements

### Requirement: GET /api/v1/admin/panel/acciones-por-dia

The system SHALL provide a `GET /api/v1/admin/panel/acciones-por-dia` endpoint that returns action volume aggregated by day within a date range.

The endpoint SHALL:
- Require authentication (`get_current_user`)
- Require permission `auditoria:ver` or `auditoria:ver(propio)`
- Accept optional query parameters:
  - `desde: datetime | None` (default: 30 days ago)
  - `hasta: datetime | None` (default: now)
  - `materia_id: str | None`
  - `actor_id: str | None`
  - `accion: str | None`
- Return a list of `{fecha: str, total: int}` objects sorted by date ascending

The `(propio)` scope SHALL filter results to materias where the current user has active assignment.

#### Scenario: Admin gets action volume by day
- **WHEN** an ADMIN sends GET /api/v1/admin/panel/acciones-por-dia
- **THEN** returns daily action counts for the last 30 days for the tenant

#### Scenario: Filter by date range
- **WHEN** GET /api/v1/admin/panel/acciones-por-dia?desde=2026-01-01&hasta=2026-01-31
- **THEN** returns daily counts only within January 2026

#### Scenario: Filter by materia
- **WHEN** GET /api/v1/admin/panel/acciones-por-dia?materia_id=<uuid>
- **THEN** returns daily counts only for that materia

#### Scenario: COORDINADOR sees only assigned materias
- **WHEN** a COORDINADOR with `auditoria:ver(propio)` sends GET /api/v1/admin/panel/acciones-por-dia
- **THEN** returns daily counts limited to materias where they have active assignment

### Requirement: GET /api/v1/admin/panel/comunicaciones-por-docente

The system SHALL provide a `GET /api/v1/admin/panel/comunicaciones-por-docente` endpoint that returns communication status aggregated by docente.

The endpoint SHALL:
- Require authentication (`get_current_user`)
- Require permission `auditoria:ver` or `auditoria:ver(propio)`
- Accept optional query parameters:
  - `desde: datetime | None`
  - `hasta: datetime | None`
  - `materia_id: str | None`
- Return a list of `{docente_id: str, docente_nombre: str, pendiente: int, enviando: int, enviado: int, fallido: int, cancelado: int}` objects

The endpoint SHALL identify communications by action codes prefixed with `COMUNICACION_` and derive status from the action code or detalle metadata.

The `(propio)` scope SHALL filter results to materias where the current user has active assignment.

#### Scenario: Admin gets communications by docente
- **WHEN** an ADMIN sends GET /api/v1/admin/panel/comunicaciones-por-docente
- **THEN** returns communication status aggregated by docente for the tenant

#### Scenario: Filter by materia
- **WHEN** GET /api/v1/admin/panel/comunicaciones-por-docente?materia_id=<uuid>
- **THEN** returns communications only for that materia

### Requirement: GET /api/v1/admin/panel/interacciones-por-docente-materia

The system SHALL provide a `GET /api/v1/admin/panel/interacciones-por-docente-materia` endpoint that returns interaction metrics by docente and materia.

The endpoint SHALL:
- Require authentication (`get_current_user`)
- Require permission `auditoria:ver` or `auditoria:ver(propio)`
- Accept optional query parameters:
  - `desde: datetime | None`
  - `hasta: datetime | None`
  - `materia_id: str | None`
  - `actor_id: str | None`
- Return a list of `{docente_id: str, docente_nombre: str, materia_id: str, materia_nombre: str, total_acciones: int, acciones_por_tipo: dict}` objects

The `(propio)` scope SHALL filter results to materias where the current user has active assignment.

#### Scenario: Admin gets interactions by docente and materia
- **WHEN** an ADMIN sends GET /api/v1/admin/panel/interacciones-por-docente-materia
- **THEN** returns interaction metrics grouped by docente and materia

#### Scenario: COORDINADOR sees only assigned materias
- **WHEN** a COORDINADOR with `auditoria:ver(propio)` sends GET /api/v1/admin/panel/interacciones-por-docente-materia
- **THEN** returns data only for their assigned materias

### Requirement: GET /api/v1/admin/panel/ultimas-acciones

The system SHALL provide a `GET /api/v1/admin/panel/ultimas-acciones` endpoint that returns the most recent audit log entries.

The endpoint SHALL:
- Require authentication (`get_current_user`)
- Require permission `auditoria:ver` or `auditoria:ver(propio)`
- Accept optional query parameters:
  - `max: int` (default: 200, max: 1000)
  - `desde: datetime | None`
  - `hasta: datetime | None`
  - `materia_id: str | None`
  - `actor_id: str | None`
  - `accion: str | None`
- Return a list of `AuditLogResponse` objects ordered by `fecha_hora DESC`

The `(propio)` scope SHALL filter results to materias where the current user has active assignment.

#### Scenario: Admin gets latest actions
- **WHEN** an ADMIN sends GET /api/v1/admin/panel/ultimas-acciones
- **THEN** returns the 200 most recent audit log entries

#### Scenario: Custom max results
- **WHEN** GET /api/v1/admin/panel/ultimas-acciones?max=50
- **THEN** returns only 50 most recent entries

#### Scenario: Max limit enforced
- **WHEN** GET /api/v1/admin/panel/ultimas-acciones?max=5000
- **THEN** returns at most 1000 entries (max enforced)

#### Scenario: Filtered by action type
- **WHEN** GET /api/v1/admin/panel/ultimas-acciones?accion=CALIFICACIONES_IMPORTAR
- **THEN** returns only entries with that action code
