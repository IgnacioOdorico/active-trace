## 1. Modelo y migración

- [x] 1.1 Crear `backend/app/models/comunicacion.py` con `Comunicacion(Base, EntityMeta)`: id, tenant_id, enviado_por, materia_id, destinatario (String(500)), asunto (String(200)), cuerpo (Text), lote_id (UUID nullable), intentos (int default 0), error_msg (Text nullable), estado (String(30)), enviado_at (DateTime nullable), enqueue_at (DateTime nullable). Incluir enum Python `EstadoComunicacion` con estados: Nueva, PendienteAprobacion, Pendiente, Enviando, Enviado, Error, Cancelado.
- [x] 1.2 Añadir columna `requiere_aprobacion_comunicaciones` (Boolean, default false) al modelo `Tenant`.
- [x] 1.3 Registrar `Comunicacion` en `backend/app/models/__init__.py`.
- [x] 1.4 Crear migración Alembic `009` con tabla `comunicacion` y ALTER TABLE tenant.

## 2. Repositorio

- [x] 2.1 Crear `backend/app/repositories/comunicacion_repository.py` con `ComunicacionRepository(BaseRepository[Comunicacion])`: métodos `get_pendientes(limit, session)` (estado=Pendiente, ordered by created_at), `get_by_lote(lote_id, session)`, `batch_update_estado(lote_id, estado_origen, estado_destino, session)`, `count_by_lote(lote_id, session)`.
- [x] 2.2 Registrar en `backend/app/repositories/__init__.py`.

## 3. Service — ComunicacionService

- [x] 3.1 Crear `backend/app/services/comunicacion_service.py` con `ComunicacionService`: inyecta `ComunicacionRepository`, `AuditLogService`, `TenantRepository` (para leer flag aprobación).
- [x] 3.2 Implementar máquina de estados en `_transiciones_validas` (dict con transiciones permitidas por D4 del design) y método `_validar_transicion(estado_actual, estado_destino)`.
- [x] 3.3 Implementar `preview(materia_id, destinatario_email, asunto_template, cuerpo_template, db)`: busca entrada en padrón activo, sustituye variables con `string.Template`, retorna asunto+cuerpo renderizados. Sin persistencia.
- [x] 3.4 Implementar `enviar(materia_id, destinatarios, asunto_template, cuerpo_template, usuario_id, db)`: genera `lote_id`, por cada destinatario cifra email con `security.encrypt()`, crea `Comunicacion` con estado Pendiente (o PendienteAprobacion según tenant), registra audit log `COMUNICACION_ENVIAR`.
- [x] 3.5 Implementar `aprobar_lote(lote_id, db)`: transiciona PendienteAprobacion → Pendiente para todas las comunicaciones del lote. Registra audit log.
- [x] 3.6 Implementar `rechazar_lote(lote_id, db)`: transiciona PendienteAprobacion → Cancelado. Registra audit log.
- [x] 3.7 Implementar `aprobar_comunicacion(comunicacion_id, db)`: transiciona una comunicación individual PendienteAprobacion → Pendiente.
- [x] 3.8 Implementar `cancelar(comunicacion_id, db)`: transiciona Pendiente/PendienteAprobacion → Cancelado.
- [x] 3.9 Implementar `listar(filtros, pagina, por_pagina, db)`: lista paginada con filtros por lote_id, materia_id, estado. Descifra destinatario.
- [x] 3.10 Implementar `obtener(comunicacion_id, db)`: retorna comunicación por ID con destinatario descifrado.
- [x] 3.11 Implementar `listar_lotes(db)`: agrupa por lote_id, retorna total y conteo por estado.
- [x] 3.12 Implementar `procesar_cola(db, proveedor_envio)` (usado por worker): obtiene pendientes, por cada una: UPDATE atómico a Enviando, ejecuta envío, si ok → Enviado, si error → Pendiente (intentos < 3) o Error (intentos >= 3). Registra audit log en estado final.

## 4. Worker

- [x] 4.1 Crear `backend/app/workers/comunicacion_worker.py` con `ComunicacionWorker`: loop asyncio con intervalo configurable (`WORKER_POLL_INTERVAL`, default 10s), obtiene session DB, llama a `ComunicacionService.procesar_cola()`. Maneja graceful shutdown con señal SIGTERM.
- [x] 4.2 Actualizar `backend/app/workers/main.py` para arrancar `ComunicacionWorker` además del placeholder actual (o reemplazar el placeholder).
- [x] 4.3 Implementar proveedor de envío mock/stub para desarrollo: `MockProveedorEnvio` que simula éxito/error según regla configurable (para tests).

## 5. Schemas

- [x] 5.1 Crear `backend/app/schemas/comunicacion.py` con modelos Pydantic: `ComunicacionResponse`, `ComunicacionListResponse`, `CrearComunicacionRequest`, `PreviewRequest`, `PreviewResponse`, `LoteResponse`, `AprobarLoteRequest`, `EstadoCount`.

## 6. Router

- [x] 6.1 Crear `backend/app/routers/comunicaciones.py` con `APIRouter(prefix="/api/comunicaciones")`.
- [x] 6.2 Endpoint `POST /preview` — guard `comunicacion:enviar` → `ComunicacionService.preview()`.
- [x] 6.3 Endpoint `POST /enviar` — guard `comunicacion:enviar` → `ComunicacionService.enviar()`.
- [x] 6.4 Endpoint `GET /` — guard `comunicacion:enviar` → `ComunicacionService.listar()`.
- [x] 6.5 Endpoint `GET /{id}` — guard `comunicacion:enviar` → `ComunicacionService.obtener()`.
- [x] 6.6 Endpoint `POST /{id}/cancelar` — guard `comunicacion:enviar` → `ComunicacionService.cancelar()`.
- [x] 6.7 Endpoint `GET /lotes` — guard `comunicacion:enviar` → `ComunicacionService.listar_lotes()`.
- [x] 6.8 Endpoint `POST /lotes/{lote_id}/aprobar` — guard `comunicacion:aprobar` → `ComunicacionService.aprobar_lote()`.
- [x] 6.9 Endpoint `POST /lotes/{lote_id}/rechazar` — guard `comunicacion:aprobar` → `ComunicacionService.rechazar_lote()`.
- [x] 6.10 Endpoint `POST /{id}/aprobar` — guard `comunicacion:aprobar` → `ComunicacionService.aprobar_comunicacion()`.
- [x] 6.11 Registrar `comunicaciones_router` en `app/main.py`.

## 7. Permisos

- [x] 7.1 Verificar/crear los permisos `comunicacion:enviar` y `comunicacion:aprobar` en el seed/catálogo de permisos si no existen.

## 8. Tests

- [x] 8.1 Tests de máquina de estados: transiciones válidas (Nueva→Pendiente, Pendiente→Enviando, Enviando→Enviado, Enviando→Error, Pendiente→Cancelado, PendienteAprobacion→Pendiente, PendienteAprobacion→Cancelado) y transiciones inválidas (Nueva→Enviado, Cancelado→Pendiente, Enviado→Pendiente, etc.).
- [x] 8.2 Tests de preview: preview exitoso con sustitución de variables, preview con destinatario no encontrado → 422, preview es solo lectura.
- [x] 8.3 Tests de envío: envío masivo crea N comunicaciones con mismo lote_id, destinatario cifrado en DB, descifrado en response, tenant sin aprobación → Pendiente, tenant con aprobación → PendienteAprobacion.
- [x] 8.4 Tests de aprobación: aprobar lote completo, rechazar lote, aprobar individual, 403 sin permiso, 422 si ya en estado final.
- [x] 8.5 Tests de cancelación: cancelar Pendiente ok, cancelar Enviado → 422.
- [x] 8.6 Tests de worker: procesa Pendiente→Enviado, reintenta < 3, marca Error ≥ 3, optimistic lock no duplica procesamiento.
- [x] 8.7 Tests de cifrado: destinatario cifrado al crear, descifrado al leer.

## 9. Verificación

- [x] 9.1 `pytest` — todos los tests pasan.
- [x] 9.2 `ruff check .` — sin errores en código nuevo.
