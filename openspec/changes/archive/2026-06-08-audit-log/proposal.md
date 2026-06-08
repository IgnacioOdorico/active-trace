## Why

The system logs actions (RN-23) but has no structured audit infrastructure — no append-only model, no standardized action codes, no reusable decorator, and no impersonation-aware logging. Without C-05, audit requirements are unmet: every action loses traceability, impersonation is invisible, and compliance (Objetivos #4, #10) is impossible to verify.

## What Changes

- New `AuditLog` model (E-AUD) — append-only at DB and app level (no update, no delete, no soft-delete)
- New `AuditLogService` with a `log()` helper and a `@audit_log` decorator for recording actions with standardized codes
- New `audit_logger` utility function — one-liner callable from any service
- Impersonation support: `impersonado_id` field, `IMPERSONACION_INICIAR` / `IMPERSONACION_FINALIZAR` action codes, session distinguishable via middleware
- Migration 005: `audit_log` table (no reference to EntityMeta — no updated_at/deleted_at)
- API endpoints: `GET /api/v1/admin/audit-log` (list, filterable, paginated)
- Permission seeds already present: `auditoria:ver`, `auditoria:ver(propio)` (from C-04)
- New `impersonacion:usar` permission added to ADMIN seed

## Capabilities

### New Capabilities
- `audit-log-model`: `AuditLog` entity + migration + Pydantic schemas (append-only)
- `audit-log-service`: `AuditLogService` + `audit_log` decorator + `log_action` helper
- `audit-log-api`: Filtered, paginated read-only API endpoints
- `impersonation-audit`: Impersonation session tracking, middleware flag, `impersonacion:usar` permission seed

### Modified Capabilities
<!-- No existing capabilities change their specification — this is entirely new. -->

## Impact

- New model `AuditLog` in `app/models/audit_log.py` (NOT inheriting `EntityMeta`)
- New migration `005_create_audit_log.py`
- New schema in `app/schemas/audit.py`
- New service in `app/services/audit_log_service.py`
- New router in `app/api/v1/routers/audit.py`
- `app/models/__init__.py`, `app/services/__init__.py`, `alembic/env.py`, `app/main.py` — register new modules
- `app/core/seed.py` — add `impersonacion:usar` to ADMIN role
- `app/core/dependencies.py` — new `current_session` dependency for impersonation context
- The model does NOT use `EntityMeta` — it's standalone with only `id`, `tenant_id`, `created_at` (no `updated_at`, no `deleted_at`, no soft-delete)
