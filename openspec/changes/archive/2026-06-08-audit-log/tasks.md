## 1. Model

- [x] 1.1 Create `AuditLog` model in `backend/app/models/audit_log.py` with standalone columns: `id`, `tenant_id`, `fecha_hora`, `actor_id`, `impersonado_id` (nullable), `materia_id` (nullable), `accion`, `detalle` (JSON, nullable), `filas_afectadas`, `ip` (nullable), `user_agent` (nullable). NOT inheriting `EntityMeta` — no `updated_at`, no `deleted_at`
- [x] 1.2 Add FK relationships: `actor` → `User`, `impersonado` → `User` (nullable), `materia` → `Materia` (nullable)
- [x] 1.3 Create migration `005_create_audit_log.py` with table creation, FK constraints, and indexes on `(tenant_id, accion)`, `(tenant_id, actor_id)`, `(tenant_id, fecha_hora)`

## 2. Schemas

- [x] 2.1 Create `backend/app/schemas/audit.py` with `AuditLogResponse` (id as str, all fields), `AuditLogFilter` (optional: actor_id, materia_id, accion, desde, hasta, pagina, por_pagina), and `PaginatedAuditLogResponse` (items, total, pagina, por_pagina, total_paginas)

## 3. Repository Layer

- [x] 3.1 Add `AuditLogRepository` or restrict `BaseRepository[AuditLog]` to only expose `create()` and read methods — no `update()`, `delete()`, `soft_delete()`

## 4. Service Layer

- [x] 4.1 Create `AuditLogService` with action code constants (`CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `COMUNICACION_ENVIAR`, `ASIGNACION_MODIFICAR`, `LIQUIDACION_CERRAR`, `IMPERSONACION_INICIAR`, `IMPERSONACION_FINALIZAR`)
- [x] 4.2 Implement `log()` method accepting `db`, `actor_id`, `accion`, `impersonado_id`, `materia_id`, `detalle`, `filas_afectadas`, `ip`, `user_agent`
- [x] 4.3 Implement `list()` method with filters (actor_id, materia_id, accion, date range) and pagination
- [x] 4.4 Create `log_action()` free function as utility helper in the service module
- [x] 4.5 Create `@audit_log(accion="...")` decorator that captures user context and request details automatically

## 5. API Endpoints

- [x] 5.1 Create `backend/app/api/v1/routers/audit.py` with `GET /api/v1/admin/audit-log` endpoint
- [x] 5.2 Implement filtering: `actor_id`, `materia_id`, `accion`, `desde`, `hasta` query params
- [x] 5.3 Implement pagination: `pagina` and `por_pagina` query params (default 50, max 200)
- [x] 5.4 Apply `require_permission("auditoria:ver")` — with fallback to `auditoria:ver(propio)` for own-scope users
- [x] 5.5 Extract `ip` and `user_agent` from request and pass to service

## 6. Impersonation

- [x] 6.1 Add `impersonacion:usar` to ADMIN seed in `backend/app/core/seed.py` and migration 003 list
- [x] 6.2 Add `impersonating`, `impersonator_id`, `impersonated_user_id`, `original_roles` fields to JWT payload in auth service
- [x] 6.3 Expose impersonation context from `get_current_user` dependency so downstream code can read `impersonator_id` and `impersonated_user_id`
- [x] 6.4 Implement impersonation start/end endpoints that create `IMPERSONACION_INICIAR` / `IMPERSONACION_FINALIZAR` audit entries
- [x] 6.5 Ensure every `log_action()` call during impersonation records both `actor_id` (impersonator) and `impersonado_id` (impersonated user)

## 7. Registration

- [x] 7.1 Register `AuditLog` in `backend/app/models/__init__.py`
- [x] 7.2 Register `AuditLogService` in `backend/app/services/__init__.py`
- [x] 7.3 Import `AuditLog` in `backend/alembic/env.py`
- [x] 7.4 Register audit router in `backend/app/main.py`

## 8. Final Verification

- [x] 8.1 Run migration 005 on test database — migration file validated as valid Python with correct revision/down_revision
- [x] 8.2 Verify lint and type checks pass
- [x] 8.3 Run full test suite — all tests green
