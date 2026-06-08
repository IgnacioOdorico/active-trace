## Context

Active Trace has authorization (C-04) but zero audit infrastructure. The knowledge base defines E-AUD (AuditLog), RN-23 (every meaningful action must be logged), and RN-41 (impersonation tracking). The seed already includes `auditoria:ver` and `auditoria:ver(propio)`. The codebase has established patterns: `EntityMeta` base, `BaseRepository[T]`, service classes, Pydantic v2 schemas, and FastAPI routers with `require_permission`.

The key architectural constraint: `AuditLog` MUST be append-only — no update, no delete, no soft-delete. This means it CANNOT use `EntityMeta` (which includes `updated_at` and `deleted_at`). A standalone model is required.

## Goals / Non-Goals

**Goals:**
- Append-only `AuditLog` model with all fields from E-AUD
- `AuditLogService` with `log()` method and action code constants
- `log_action()` helper callable from any service layer
- `@audit_log` decorator for automatic context capture
- `GET /api/v1/admin/audit-log` with filters and pagination
- Impersonation tracking: JWT claim, session context, audit events
- `impersonacion:usar` permission for ADMIN role
- Migration 005 with proper FK constraints and indexes

**Non-Goals:**
- No UI for audit log (API only)
- No automatic audit of existing actions (C-05 provides infrastructure; existing services get audit in separate changes)
- No data retention/purging policy (future concern)
- No real-time streaming of audit events
- No change to existing `EntityMeta` or `BaseRepository`

## Decisions

**D1 — Standalone model (not EntityMeta):** `AuditLog` does NOT inherit `EntityMeta`. Rationale: `EntityMeta` provides `updated_at` and `deleted_at` for soft-delete, which violates the append-only requirement. Instead, a minimal base with only `id`, `tenant_id`, and `fecha_hora` is used. The model file defines its own columns explicitly.

**D2 — BaseRepository with restricted interface:** The `AuditLogService` uses `BaseRepository[AuditLog]` internally but only calls `create()`. No `update()`, `delete()`, or `soft_delete()` methods are exposed. The repository itself can still be used generically; the restriction is at the service layer. Alternative considered: a custom `AuditLogRepository` that inherits from `BaseRepository` and overrides mutating methods to raise errors. Rejected because: (1) it adds a class for no runtime benefit, (2) the service layer is the correct enforcement boundary, (3) tests catch any misuse.

**D3 — `log_action()` as free function, `@audit_log` as decorator:** The free function is for service-to-service calls where the caller has explicit control over parameters. The decorator is for route handlers or service methods where context (user, IP, user_agent) can be captured automatically via `request: Request` injection. Alternative considered: only a decorator. Rejected because services (like `CarreraService.create()`) shouldn't depend on FastAPI's `Request` object.

**D4 — Impersonation via JWT claims, not DB session:** Impersonation state is carried in the JWT payload (`impersonating`, `impersonator_id`, `impersonated_user_id`). The `get_current_user` dependency reads these claims and attaches the impersonation context to the user object. Alternative considered: a server-side session store (Redis). Rejected because JWT claims are simpler, stateless, and sufficient for short-lived impersonation sessions (token TTL bounds impersonation duration).

**D5 — IP and user_agent captured at the API layer:** The router handler extracts `request.client.host` and `request.headers.get("user-agent")` and passes them to `log_action()`. The decorator does this automatically. Services (business logic) don't know about HTTP details — they receive `ip` and `user_agent` as optional parameters.

**D6 — Pagination with manual SQL:** The `GET /audit-log` endpoint uses raw offset/limit pagination via `BaseRepository`'s `get_all()` pattern. Alternative considered: keyset pagination for better performance on large datasets. Rejected for now because: (1) the audit log is per-tenant, not global, so volumes are bounded, (2) offset pagination matches the existing pattern in the codebase, (3) keyset pagination can be added later without breaking changes.

## Risks / Trade-offs

- [Audit log table growth] Append-only means the table grows unboundedly. Mitigation: indexes on `(tenant_id, fecha_hora)` support efficient time-range queries. A data retention/purging policy will be added as a future change.
- [Impersonation JWT misuse] If a JWT with `impersonating=true` leaks, an attacker could impersonate. Mitigation: short TTL (15 min), and impersonation is only available to ADMIN role.
- [Decorator hides complexity] The `@audit_log` decorator automatically captures user context, which could make audit logging "invisible" to developers. Mitigation: clear documentation and naming convention (`@audit_log(accion="...")` is explicit about what action is logged).
- [No hard-delete on audit_log] Unlike other tables, `audit_log` has no `deleted_at`. This means the `BaseRepository._base_query()` pattern (which filters `deleted_at.is_(None)`) shouldn't be used. Mitigation: `AuditLogService` uses a dedicated query that doesn't filter on `deleted_at`.
