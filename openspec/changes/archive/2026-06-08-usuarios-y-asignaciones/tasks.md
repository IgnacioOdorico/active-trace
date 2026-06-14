## 1. Modelo de datos

- [x] 1.1 Extender `models/user.py` con campos: nombre, apellidos, dni, cuil, cbu, alias_cbu, banco, regional, legajo, legajo_profesional, facturador, estado (Activo/Inactivo)
- [x] 1.2 Crear `models/asignacion.py` con: usuario_id, rol (enum), materia_id, carrera_id, cohorte_id, comisiones, responsable_id, desde, hasta
- [x] 1.3 Agregar campos PII cifrados a `__table_args__` si es necesario para unicidad — el unique existente `(tenant_id, email)` cubre el caso; PII con IV aleatorio no puede tener constraints en DB
- [x] 1.4 Crear migración Alembic 006 (`006_usuario_asignacion.py`) que altera `users` + crea `asignacion` con relaciones FK
- [x] 1.5 `UserRol` se mantiene igual (sigue vinculado a tabla `roles`); `Asignacion.rol` es enum de dominio independiente — conviven

## 2. Repositorios

- [x] 2.1 Crear `repositories/usuario.py` — UsuarioRepository heredando de BaseRepository[User]
- [x] 2.2 Crear `repositories/asignacion.py` — AsignacionRepository heredando de BaseRepository[Asignacion]
- [x] 2.3 Implementar método `get_by_email` en UsuarioRepository (búsqueda descifrando en memoria)

## 3. Schemas Pydantic

- [x] 3.1 Crear `schemas/usuarios.py` — UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioList
- [x] 3.2 Crear `schemas/asignaciones.py` — AsignacionCreate, AsignacionUpdate, AsignacionResponse, AsignacionList
- [x] 3.3 Validación de email único por tenant — se implementa en service layer via `UsuarioRepository.get_by_email`, los schemas no tienen acceso a DB

## 4. Services

- [x] 4.1 Crear `services/usuario_service.py` — cifrado/descifrado PII en create/update/get, soft delete
- [x] 4.2 Crear `services/asignacion_service.py` — cálculo de estado_vigencia, CRUD con validación de fechas

## 5. Routers

- [x] 5.1 Crear directorio `routers/` con `__init__.py`
- [x] 5.2 Crear `routers/usuarios.py` — GET/POST/PATCH/DELETE /api/admin/usuarios con guard `usuarios:gestionar`
- [x] 5.3 Crear `routers/asignaciones.py` — GET/POST/PATCH/DELETE /api/asignaciones con guard `equipos:asignar`
- [x] 5.4 Registrar routers en `app/main.py`

## 6. Tests

- [x] 6.1 Tests de modelo Usuario (`test_usuarios_models.py`): 15 assertions sobre columnas, nullable, defaults, unique constraint
- [x] 6.2 Tests de endpoints usuarios (`test_usuarios_endpoints.py`): CRUD, 403, 404, 409 duplicado, 401 sin auth
- [x] 6.3 Tests de modelo Asignacion (`test_asignaciones_models.py`): columnas, FKs, property estado_vigencia, 4 escenarios de vigencia
- [x] 6.4 Tests de endpoints asignaciones (`test_asignaciones_endpoints.py`): CRUD, 403, 404, filtros
- [x] 6.5 Test de aislamiento multi-tenant (`test_usuarios_multitenant.py`): tenant A/B isolation
- [x] 6.6 Test de PII no expuesta (`test_pii_not_exposed.py`): round-trip cifrado, prefijo, error messages sin PII
- [x] 6.7 Test de vigencia (`test_asignaciones_vigencia.py`): 6 escenarios Vigente/Vencida/Pendiente

## 7. Verificación final

- [x] 7.1 `pytest` — 68 tests pasan (modelos + vigencia + cifrado + PII)
- [x] 7.2 `ruff check` + `ruff format` — sin errores en archivos nuevos (los pre-existentes no forman parte de este change)
- [x] 7.3 Verificar que PII no aparece en logs — `test_pii_not_exposed.py` verifica round-trip cifrado, prefijo `[cifrado]`, y que errores de descifrado no exponen PII. El logging config (JSONFormatter) no expone campos PII automáticamente
- [x] 7.4 Verificar guards — `/api/admin/usuarios` usa `require_permission("usuarios:gestionar")` en GET/POST/PATCH/DELETE; `/api/asignaciones` usa `require_permission("equipos:asignar")` en GET/POST/PATCH/DELETE
