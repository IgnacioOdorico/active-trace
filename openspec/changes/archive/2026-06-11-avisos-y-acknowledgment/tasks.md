## 1. Modelos y migración

- [x] 1.1 Crear `backend/app/models/aviso.py` con `Aviso(Base, EntityMeta)`: id, tenant_id, alcance (String(20)), materia_id (UUID nullable FK), cohorte_id (UUID nullable FK), rol_destino (String(20) nullable), severidad (String(20)), titulo (String(200)), cuerpo (Text), inicio_en (DateTime), fin_en (DateTime), orden (Integer), activo (Boolean default True), requiere_ack (Boolean default False). Incluir enums Python `AlcanceAviso` y `SeveridadAviso`.
- [x] 1.2 Crear `backend/app/models/acknowledgment_aviso.py` con `AcknowledgmentAviso(Base, EntityMeta)`: id, aviso_id (UUID FK), usuario_id (UUID FK), confirmado_at (DateTime).
- [x] 1.3 Registrar ambos modelos en `backend/app/models/__init__.py`.
- [x] 1.4 Crear migración Alembic con tablas `aviso` y `acknowledgment_aviso`.

## 2. Repositorios

- [x] 2.1 Crear `backend/app/repositories/aviso_repository.py` con `AvisoRepository(BaseRepository[Aviso])`: método `list_visibles(tenant_id, usuario_id, roles, materia_ids, cohorte_ids, pagina, page_size, db)` con filtros combinados de alcance/vigencia/activo, método `list_gestion(filtros, pagina, page_size, db)` para ABM (incluye no activos).
- [x] 2.2 Crear `backend/app/repositories/acknowledgment_aviso_repository.py` con `AcknowledgmentAvisoRepository(BaseRepository[AcknowledgmentAviso])`: método `contar_por_aviso(aviso_id, db)`, método `existe(aviso_id, usuario_id, db)` para idempotencia, método `crear(aviso_id, usuario_id, db)`.
- [x] 2.3 Registrar ambos repositorios en `backend/app/repositories/__init__.py`.

## 3. Schemas

- [x] 3.1 Crear `backend/app/schemas/aviso.py` con modelos Pydantic: `AvisoResponse`, `AvisoCreateRequest`, `AvisoUpdateRequest`, `AvisoListResponse`, `AcknowledgmentResponse`, `ContadorResponse`.

## 4. Service — AvisoService

- [x] 4.1 Crear `backend/app/services/aviso_service.py` con `AvisoService`: inyecta `AvisoRepository`, `AcknowledgmentAvisoRepository`, `AuditLogService`.
- [x] 4.2 Implementar `crear(data, usuario_id, db)`: crea aviso, registra audit log `AVISO_PUBLICAR`.
- [x] 4.3 Implementar `editar(aviso_id, data, usuario_id, db)`: actualiza aviso existente, registra audit log `AVISO_EDITAR`.
- [x] 4.4 Implementar `eliminar(aviso_id, usuario_id, db)`: soft delete, registra audit log `AVISO_ELIMINAR`.
- [x] 4.5 Implementar `listar_visibles(usuario, db)`: obtiene materias/cohortes del usuario, filtra avisos por perfil + vigencia + activo, ordena por orden ascendente.
- [x] 4.6 Implementar `listar_gestion(filtros, pagina, page_size, db)`: listado paginado con contador de acknowledgments, para ABM.
- [x] 4.7 Implementar `obtener(aviso_id, db)`: detalle de aviso con contador de acknowledgments.
- [x] 4.8 Implementar `confirmar_lectura(aviso_id, usuario_id, db)`: crea AcknowledgmentAviso con idempotencia (si ya existe, retorna éxito).

## 5. Routers

- [x] 5.1 Crear `backend/app/routers/avisos.py` con `APIRouter(prefix="/api/avisos")`.
- [x] 5.2 Endpoint `POST /` — guard `avisos:publicar` → `AvisoService.crear()`.
- [x] 5.3 Endpoint `GET /` — sin permiso explícito (todos ven sus avisos) → `AvisoService.listar_visibles()`.
- [x] 5.4 Endpoint `GET /gestion` — guard `avisos:publicar` → `AvisoService.listar_gestion()`. (Definir ANTES de `GET /{id}`).
- [x] 5.5 Endpoint `GET /{id}` — guard `avisos:publicar` → `AvisoService.obtener()`.
- [x] 5.6 Endpoint `PATCH /{id}` — guard `avisos:publicar` → `AvisoService.editar()`.
- [x] 5.7 Endpoint `DELETE /{id}` — guard `avisos:publicar` → `AvisoService.eliminar()`.
- [x] 5.8 Endpoint `POST /{id}/ack` — sin permiso explícito → `AvisoService.confirmar_lectura()`.
- [x] 5.9 Registrar router `avisos` en `app/main.py`.

## 6. Permisos

- [x] 6.1 Crear permiso `avisos:publicar` en el seed/catálogo de permisos.
- [x] 6.2 Asignar `avisos:publicar` a roles COORDINADOR y ADMIN.

## 7. Audit

- [x] 7.1 Agregar constantes `AVISO_PUBLICAR`, `AVISO_EDITAR`, `AVISO_ELIMINAR` en `AuditLogService`.

## 8. Tests

- [x] 8.1 Tests de ABM avisos: crear, editar, soft delete, permisos, 404 en inexistente.
- [x] 8.2 Tests de visualización por perfil: alcance Global, PorMateria, PorCohorte, PorRol, exclusión por vigencia, orden de prioridad, aviso inactivo no se muestra.
- [x] 8.3 Tests de acknowledgment: confirmar lectura, idempotencia (doble ack), 404 en aviso inexistente.
- [x] 8.4 Tests de gestión: listado paginado, contador de acknowledgments.
- [x] 8.5 Tests de auditoría: verificar audit log en crear, editar, eliminar.

## 9. Verificación

- [x] 9.1 `pytest` — todos los tests pasan.
- [x] 9.2 `ruff check .` — sin errores en código nuevo.
