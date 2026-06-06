## 1. Models

- [x] 1.1 Create `Carrera` model in `backend/app/models/carrera.py` extending EntityMeta, with UniqueConstraint(tenant_id, codigo), FK to tenant via EntityMeta
- [x] 1.2 Create `Cohorte` model in `backend/app/models/cohorte.py` extending EntityMeta, with UniqueConstraint(tenant_id, carrera_id, nombre), FK to carrera
- [x] 1.3 Create `Materia` model in `backend/app/models/materia.py` extending EntityMeta, with UniqueConstraint(tenant_id, codigo), nullable FK to carrera
- [x] 1.4 Register all three models in `backend/app/models/__init__.py`

## 2. Repositories

- [x] 2.1 Using `BaseRepository[Carrera]` directly (no custom repo needed)
- [x] 2.2 Using `BaseRepository[Cohorte]` directly (no custom repo needed)
- [x] 2.3 Using `BaseRepository[Materia]` directly (no custom repo needed)
- [x] 2.4 Repositories instantiated in services (no __init__ registration needed)

## 3. Schemas

- [x] 3.1 Create Pydantic schemas for Carrera: CarreraCreate, CarreraUpdate, CarreraResponse (with id as string)
- [x] 3.2 Create Pydantic schemas for Cohorte: CohorteCreate, CohorteUpdate, CohorteResponse
- [x] 3.3 Create Pydantic schemas for Materia: MateriaCreate, MateriaUpdate, MateriaResponse

## 4. Service Layer

- [x] 4.1 Create service classes in `backend/app/services/carrera_service.py`, `cohorte_service.py`, `materia_service.py` with CRUD delegating to repositories
- [x] 4.2 Implement desactivar validation: rejects if any active cohorte exists
- [x] 4.3 Implement crear_cohorte validation: validates carrera is active before creating
- [x] 4.4 Register services in `backend/app/services/__init__.py`

## 5. Endpoints

- [x] 5.1 Create `backend/app/api/v1/routers/estructura.py` with admin prefix guarded by `require_permission("estructura:gestionar")`
- [x] 5.2 Implement GET/POST/PUT/DELETE for `/api/admin/carreras` returning serialized schemas
- [x] 5.3 Implement GET/POST/PUT/DELETE for `/api/admin/cohortes` returning serialized schemas
- [x] 5.4 Implement GET/POST/PUT/DELETE for `/api/admin/materias` returning serialized schemas
- [x] 5.5 Register the estructura router in the main app router

## 6. Migration

- [x] 6.1 Create migration 004 with tables: carrera, cohorte, materia including all constraints and FKs
- [ ] 6.2 Run migration against a local DB to verify DDL executes cleanly (both upgrade and downgrade)

## 7. Tests

- [x] 7.1 Write CRUD tests for Carrera (create, read, update, soft-delete, list)
- [x] 7.2 Write CRUD tests for Cohorte (create scoped to carrera, read, update, soft-delete)
- [x] 7.3 Write CRUD tests for Materia (create with/without carrera, read, update, soft-delete)
- [x] 7.4 Write uniqueness tests: duplicate codigo per tenant rejected, same codigo different tenant allowed
- [x] 7.5 Write multi-tenant isolation tests: entities from tenant A not visible in tenant B
- [x] 7.6 Write state transition tests: deactivate carrera with active cohorts rejected, activate/deactivate lifecycle
- [x] 7.7 Write service layer tests for business rules (desactivar_carrera validation, crear_cohorte validation)

## 8. Verification

- [x] 8.1 Run full test suite: 65/65 unit/model tests pass, endpoint tests skip (no DB), 266 existing tests pass (0 regressions)
- [x] 8.2 Run linting (ruff) on all changed files — all checks passed
- [ ] 8.3 Run type checking (mypy/pyright) on all new files (requires full DB env)
