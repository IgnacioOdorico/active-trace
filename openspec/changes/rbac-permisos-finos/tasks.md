## 1. Models

- [x] 1.1 Create Rol model (UUID pk, codigo unique, nombre, descripcion, activo, EntityMeta)
- [x] 1.2 Create Permiso model (UUID pk, codigo unique "modulo:accion", nombre, descripcion, propio bool, EntityMeta)
- [x] 1.3 Create RolPermiso association model (Rol FK, Permiso FK, unique constraint, ambito nullable)
- [x] 1.4 Add relationships: Rol.permisos (M2M through RolPermiso), Permiso.roles (M2M through RolPermiso)

## 2. Seed Data

- [x] 2.1 Define seed data module with all 7 canonical roles and their permission matrix from 03_actores_y_roles.md §3.3
- [x] 2.2 Define all Permiso entries referenced by the 7 roles

## 3. Auth Service Update

- [x] 3.1 Modify `create_access_token` to accept `roles: list[str]` parameter and include `"rols"` claim in JWT payload
- [x] 3.2 Update login endpoint to resolve user's role assignments and pass them to `create_access_token`
- [x] 3.3 Add roles relationship to User model

## 4. Permission Guard

- [x] 4.1 Create `require_permission(codigo: str)` dependency factory with RolPermiso DB lookup
- [x] 4.2 Implement wildcard matching (`*` in modulo or accion)
- [x] 4.3 Implement `(propio)` scope via optional `own_resource_check: Callable` parameter
- [x] 4.4 Export guard from app/api/dependencies.py or new app/core/authorization.py

## 5. Admin Catalog Endpoints

- [x] 5.1 Create admin router at app/api/v1/routers/admin.py with prefix `/api/v1/admin`
- [x] 5.2 Implement `GET/POST /roles` and `PUT/DELETE /roles/{rol_id}` endpoints
- [x] 5.3 Implement `GET/POST /permisos` endpoints
- [x] 5.4 Implement `POST /roles/{rol_id}/permisos` and `DELETE /roles/{rol_id}/permisos/{permiso_id}` endpoints
- [x] 5.5 Register admin router in app

## 6. Migration

- [x] 6.1 Generate Alembic migration 003 for rol, permiso, rol_permiso tables
- [x] 6.2 Add seed data logic to migration (7 roles + full permission matrix via RolPermiso)

## 7. Tests

- [x] 7.1 Test Rol model creation, unique constraint, soft delete
- [x] 7.2 Test Permiso model with propio and wildcard codigo formats
- [x] 7.3 Test RolPermiso association and cascade behavior
- [x] 7.4 Test `require_permission` guard: user with permission → 200, without → 403
- [x] 7.5 Test `require_permission` guard: wildcard matching
- [x] 7.6 Test `require_permission` guard: propio scope check (pass and fail)
- [x] 7.7 Test JWT rols claim payload
- [x] 7.8 Test admin catalog endpoints: CRUD operations, 403 for non-admin
- [x] 7.9 Test seed data: all 7 roles and their permissions after migration

## 8. Final Verification

- [x] 8.1 Run migrations with seed data on test database
- [x] 8.2 Run full test suite — all tests green
- [x] 8.3 Verify lint and type checks pass
