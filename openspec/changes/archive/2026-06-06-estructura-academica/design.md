## Context

RBAC foundation (C-04) is complete with `estructura:*` wildcard granted to ADMIN and COORDINADOR. The `estructura:gestionar` guard is the specific permission for ABM operations. All three models are tenant-isolated catalog entities — they must share the existing tenancy patterns (EntityMeta, BaseRepository) and be consumable by downstream features (C-07 usuarios, C-08 equipos, etc.).

## Goals / Non-Goals

**Goals:**
- Tenant-scoped CRUD for Carrera, Cohorte, Materia
- Uniqueness constraints per ADR-006 (codigo unique per tenant, cohorte nombre unique per tenant+carrera)
- Business rule: inactive carrera cannot have active cohorts
- Admin endpoints guarded by `estructura:gestionar`

**Non-Goals:**
- Batch operations or bulk import
- Soft-delete cascade (each entity soft-deleted independently)
- UI or frontend changes

## Decisions

### D1: All models extend EntityMeta
All three inherit `tenant_id`, `id` (UUID PK), `created_at`, `updated_at`, `deleted_at`. This guarantees tenant isolation and consistent timestamping without duplication.

### D2: UniqueConstraint(tenant_id, codigo) on Carrera and Materia
Model-level `__table_args__` with `UniqueConstraint("tenant_id", "codigo", name="uq_carrera_codigo_per_tenant")`. Prevents cross-tenant codigo collision and enforces domain integrity per ADR-006.

### D3: UniqueConstraint(tenant_id, carrera_id, nombre) on Cohorte
Cohorte `nombre` is meaningful only within a carrera context: `UniqueConstraint("tenant_id", "carrera_id", "nombre", name="uq_cohorte_nombre_per_carrera")`.

### D4: BaseRepository[T] for all CRUD
Follows the C-02 pattern. Repositories accept `tenant_id` at construction, providing automatic tenant scoping via `_base_query()`. Methods: `create`, `get`, `get_all`, `update`, `soft_delete`, `count`.

### D5: Service layer for business rules
`EstructuraService` wraps repository calls and enforces cross-entity rules:
- `desactivar_carrera()` checks no active cohorts exist before deactivating
- `crear_cohorte()` validates carrera is active
Services depend on repositories, not directly on the session.

### D6: Guarded with `estructura:gestionar`
Admin ABM endpoints use `require_permission("estructura:gestionar")`. The existing `estructura:*` wildcard in seed permissions already covers COORDINADOR and ADMIN roles.

## Risks / Trade-offs

- [Soft-delete vs cascade] → Carrera soft-delete does NOT cascade. Cohorte records with `deleted_at IS NULL` referencing a soft-deleted carrera become orphaned. Downstream queries must join with `carrera.deleted_at IS NULL` filter. Acceptable because cascading soft-delete adds complexity for an edge case.
- [Codigo immutability] → `codigo` represents the institutional code. We do NOT prevent updates in the schema, but services should reject `codigo` changes on `update` to avoid referential drift. Enforced at service layer.
- [Materia.carrera_id nullable] → Some subjects are cross-carrera (e.g., "Inglés"). Making the FK nullable supports this without adding a join table.
