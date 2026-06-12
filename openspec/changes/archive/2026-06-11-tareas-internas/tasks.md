## 1. Modelos y migración

- [x] 1.1 Crear `backend/app/models/tarea.py` con `Tarea(Base, EntityMeta)`: id, tenant_id, materia_id (UUID nullable FK), asignado_a (UUID FK), asignado_por (UUID FK), estado (String(20), default "Pendiente"), descripcion (Text), contexto_id (UUID nullable). Incluir enum Python `EstadoTarea` con Pendiente, En progreso, Resuelta, Cancelada.
- [x] 1.2 Crear `backend/app/models/comentario_tarea.py` con `ComentarioTarea(Base, EntityMeta)`: id, tenant_id, tarea_id (UUID FK), autor_id (UUID FK), texto (Text), creado_at (DateTime).
- [x] 1.3 Registrar ambos modelos en `backend/app/models/__init__.py`.
- [x] 1.4 Crear migración Alembic con tablas `tarea` y `comentario_tarea`.

## 2. Repositorios

- [x] 2.1 Crear `backend/app/repositories/tarea_repository.py` con `TareaRepository(BaseRepository[Tarea])`: método `list_mias(usuario_id, filtros, pagina, page_size, db)`, método `list_todas(filtros, pagina, page_size, db)` con filtros por asignado_a, asignado_por, materia_id, estado, busqueda (ILIKE en descripcion).
- [x] 2.2 Crear `backend/app/repositories/comentario_tarea_repository.py` con `ComentarioTareaRepository(BaseRepository[ComentarioTarea])`: método `list_por_tarea(tarea_id, pagina, page_size, db)`.
- [x] 2.3 Registrar ambos repositorios en `backend/app/repositories/__init__.py`.

## 3. Schemas

- [x] 3.1 Crear `backend/app/schemas/tarea.py` con modelos Pydantic: `TareaResponse`, `TareaCreateRequest`, `TareaUpdateRequest`, `TareaListResponse`, `ComentarioResponse`, `ComentarioCreateRequest`, `ComentarioListResponse`.

## 4. Service — TareaService

- [x] 4.1 Crear `backend/app/services/tarea_service.py` con `TareaService`: inyecta `TareaRepository`, `ComentarioTareaRepository`, `AuditLogService`.
- [x] 4.2 Implementar `crear(data, usuario_id, db)`: crea tarea con asignado_por=usuario_id, estado=Pendiente. Registra audit `TAREA_CREAR`.
- [x] 4.3 Implementar `editar(tarea_id, data, usuario_id, db)`: modifica campos (asignado_a, descripcion). Valida transiciones de estado si se cambia estado. Registra audit `TAREA_EDITAR`.
- [x] 4.4 Implementar `eliminar(tarea_id, db)`: soft delete.
- [x] 4.5 Implementar `listar_mias(usuario_id, filtros, pagina, page_size, db)`: tareas donde asignado_a = usuario_id.
- [x] 4.6 Implementar `listar_todas(filtros, pagina, page_size, db)`: listado global con filtros.
- [x] 4.7 Implementar `obtener(tarea_id, db)`: detalle de tarea.
- [x] 4.8 Implementar `agregar_comentario(tarea_id, texto, usuario_id, db)`: crea comentario, registra audit `TAREA_COMENTAR`.
- [x] 4.9 Implementar `listar_comentarios(tarea_id, pagina, page_size, db)`: comentarios ordenados por creado_at.

## 5. Routers

- [x] 5.1 Crear `backend/app/routers/tareas.py` con `APIRouter(prefix="/api/tareas")`.
- [x] 5.2 Endpoint `POST /` — guard `tareas:gestionar` → `TareaService.crear()`.
- [x] 5.3 Endpoint `GET /mias` — guard `tareas:gestionar` → `TareaService.listar_mias()`. (Static BEFORE `/{id}`)
- [x] 5.4 Endpoint `GET /` — guard `tareas:gestionar` → `TareaService.listar_todas()`.
- [x] 5.5 Endpoint `GET /{id}` — guard `tareas:gestionar` → `TareaService.obtener()`.
- [x] 5.6 Endpoint `PATCH /{id}` — guard `tareas:gestionar` → `TareaService.editar()`.
- [x] 5.7 Endpoint `DELETE /{id}` — guard `tareas:gestionar` → `TareaService.eliminar()`.
- [x] 5.8 Endpoint `GET /{id}/comentarios` — guard `tareas:gestionar` → `TareaService.listar_comentarios()`.
- [x] 5.9 Endpoint `POST /{id}/comentarios` — guard `tareas:gestionar` → `TareaService.agregar_comentario()`.
- [x] 5.10 Registrar router `tareas` en `app/main.py`.

## 6. Permisos

- [x] 6.1 Crear permiso `tareas:gestionar` en el seed/catálogo de permisos.
- [x] 6.2 Asignar `tareas:gestionar` a roles PROFESOR, COORDINADOR y ADMIN.

## 7. Audit

- [x] 7.1 Agregar constantes `TAREA_CREAR`, `TAREA_EDITAR`, `TAREA_COMENTAR` en `AuditLogService`.

## 8. Tests

- [x] 8.1 Tests de ABM: crear tarea, editar asignado_a, soft delete, 404, 403 sin permiso.
- [x] 8.2 Tests de transiciones de estado: Pendiente→En progreso, Pendiente→Cancelada, En progreso→Resuelta, Cancelado→Pendiente rechazado.
- [x] 8.3 Tests de mis tareas: lista tareas del usuario, filtra por estado, vacío.
- [x] 8.4 Tests de admin: listado global, filtros por asignado_a/materia/estado, búsqueda libre.
- [x] 8.5 Tests de comentarios: agregar comentario, listar hilo, 403 sin relación con tarea.
- [x] 8.6 Tests de auditoría: verificar audit log en crear, editar, comentar.

## 9. Verificación

- [x] 9.1 `pytest` — todos los tests pasan.
- [x] 9.2 `ruff check .` — sin errores en código nuevo.
