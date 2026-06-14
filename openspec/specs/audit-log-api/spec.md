## ADDED Requirements

### Requirement: GET /api/v1/admin/audit-log

The system SHALL provide a `GET /api/v1/admin/audit-log` endpoint that returns paginated audit log entries.

The endpoint SHALL:
- Require authentication (`get_current_user`)
- Require permission `auditoria:ver` (or `auditoria:ver(propio)` for non-ADMIN roles)
- Accept optional query parameters:
  - `actor_id: str | None`
  - `materia_id: str | None`
  - `accion: str | None`
  - `desde: datetime | None` (start of time range)
  - `hasta: datetime | None` (end of time range)
  - `pagina: int = 1`
  - `por_pagina: int = 50` (max 200)
- Return a paginated response with:
  - `items: list[AuditLogResponse]`
  - `total: int`
  - `pagina: int`
  - `por_pagina: int`
  - `total_paginas: int`

The `(propio)` scope SHALL filter results to only the current user's actions when the permission `auditoria:ver(propio)` is resolved instead of `auditoria:ver`.

#### Scenario: Admin lists audit logs
- **WHEN** an ADMIN sends GET /api/v1/admin/audit-log
- **THEN** returns a paginated list of all audit log entries for the tenant

#### Scenario: User with propio scope sees only own actions
- **WHEN** a COORDINADOR sends GET /api/v1/admin/audit-log with permission `auditoria:ver(propio)`
- **THEN** returns only audit entries where `actor_id` matches the current user

#### Scenario: Filter by action code
- **WHEN** GET /api/v1/admin/audit-log?accion=CALIFICACIONES_IMPORTAR
- **THEN** returns only entries with that action code

#### Scenario: Filter by date range
- **WHEN** GET /api/v1/admin/audit-log?desde=2026-01-01&hasta=2026-06-30
- **THEN** returns only entries within that date range

#### Scenario: Pagination
- **WHEN** GET /api/v1/admin/audit-log?pagina=2&por_pagina=10
- **THEN** returns page 2 with 10 items per page
- **AND** includes total count and total pages

#### Scenario: 403 without auditoria:ver permission
- **WHEN** a user without `auditoria:ver` or `auditoria:ver(propio)` sends GET /api/v1/admin/audit-log
- **THEN** returns 403 Forbidden
