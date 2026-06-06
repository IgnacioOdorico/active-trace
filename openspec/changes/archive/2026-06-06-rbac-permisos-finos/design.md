## Context

Active Trace has authentication (C-03) but zero authorization. Any authenticated user can access any endpoint across all tenants. The multi-tenant foundation (C-02) scopes data but doesn't restrict actions. We need a permission system that maps the 7 domain roles (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS) to granular `modulo:accion` permissions, with support for admin-manageable role-permission matrices and `(propio)` resource scoping.

## Goals / Non-Goals

**Goals:**
- DB-backed Rol, Permiso, RolPermiso models — admin-manageable, not hardcoded
- Seed 7 canonical roles with their full permission matrix at migration time
- `require_permission` FastAPI dependency guard → 403
- JWT carries resolved role IDs for zero-DB-hit permission checks
- `(propio)` scope: some permissions only apply to the user's own resources
- Admin CRUD endpoints for catalog management

**Non-Goals:**
- No UI for role management (API only, consumed by admin frontend later)
- No fine-grained object-level permissions (only module-level)
- No caching layer beyond per-request in-memory
- No changes to the existing User or Tenant models

## Decisions

**D1 — DB-backed catalog (not enums):** Roles and permissions live in relational tables, not Python enums. Seed data provides defaults via migration, but tenants can customize their role-permission matrix via admin CRUD. This avoids code deployments for permission changes.

**D2 — Permission code format:** `"modulo:accion"` with wildcard support. `"liquidaciones:*"` grants all actions in the liquidaciones module. The guard splits on `:` and matches left (modulo) and right (accion), supporting `*` on either side.

**D3 — Permission resolution:** `require_permission` reads user's role IDs from the JWT `roles` claim, then queries `RolPermiso` in a single join to check if any of the user's roles grant the required permission. Resolved per-request with an in-memory cache (Python dict scoped to the request) — no cross-request caching to avoid stale permission data.

**D4 — Seed roles and matrix:** Migration 003 seeds the 7 canonical roles from `03_actores_y_roles.md` §3.3 with their full permission matrix. Each role gets a UUID, a unique `codigo`, and its associated Permiso entries via `RolPermiso`.

**D5 — `(propio)` scope for resource ownership:** Some permissions (e.g., `atrasados:ver`) apply only to the user's own resources. The guard accepts an optional `own_resource_check: Callable[[Request, User], bool]` parameter. If the required permission is marked as `propio=True` in `Permiso`, the guard invokes the callable to verify ownership.

**D6 — JWT roles claim:** `create_access_token` accepts an explicit `roles: list[str]` parameter (list of role UUIDs/codes). The login endpoint resolves the user's active role assignments from `User.rol_ids` (or a roles relationship) and passes them to token creation. The JWT payload includes a `"rols"` claim containing the list of role IDs.

## Risks / Trade-offs

- [JWT size growth] Carrying role IDs in JWT increases token size. Mitigation: store only role UUIDs (36 bytes each), not full permission lists. Typical case: 1-3 roles per user.
- [Stale permissions within token lifetime] If an admin changes role-permission assignments, existing JWTs won't reflect it until refresh. Mitigation: short token TTL (15 min) and always query `RolPermiso` on guard invocation (don't rely solely on JWT claims for the permission check itself — JWT carries role IDs for lookup, not permission decisions).
- [Seed data drift] Customizations by tenants may diverge from seed defaults. Mitigation: seed data only runs on fresh installs; existing tenants are never overwritten.
- [propio scope complexity] The callable pattern is flexible but requires each endpoint to provide its own ownership check. Mitigation: provide default helpers (e.g., `own_resource_by_user_id`, `own_resource_by_tenant`).
