## Why

Without RBAC, there's no authorization — any authenticated user can do anything. C-04 is the gate that enforces who can do what in the multi-tenant system.

## What Changes

- New models: Rol, Permiso, RolPermiso (DB-backed, admin-manageable catalog)
- Seed data: 7 canonical roles (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS) with full permission matrix
- New `require_permission("modulo:accion")` FastAPI dependency guard → 403 on insufficient permissions
- Updated `create_access_token` to carry resolved role IDs in JWT claims
- Migration 003: rol, permiso, rol_permiso tables + seed data
- Admin CRUD endpoints for managing roles and permissions catalog
- Tests: model validation, guard behavior, role union resolution, propio scoping

## Capabilities

### New Capabilities

- `rbac-model`: Rol, Permiso, RolPermiso entities, relationships, and seed data strategy
- `permission-guard`: require_permission FastAPI dependency, permission resolution from JWT claims, (propio) scope checking
- `admin-catalog`: CRUD endpoints for managing roles and permissions (admin-only)

### Modified Capabilities

<!-- No existing capabilities are modified — this is a new concern. -->

## Impact

- New Alembic migration (003)
- `app/core/auth.py`: create_access_token signature changes (new `roles` parameter)
- `app/api/v1/routers/auth.py`: login endpoint must resolve and pass roles
- New dependency in `app/api/dependencies.py` (or new guard module)
- 403 responses introduced across the API
- Admin-only endpoints in a new router
