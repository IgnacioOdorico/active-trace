## Context

El backend (FastAPI async + SQLAlchemy 2.0, multi-tenant) ya tiene C-01 a C-19 implementados. El modelo `User` existe con campos editables y PII encriptada, y `POST /api/auth/logout` de C-03 ya invalida refresh tokens. No existe mecanismo de mensajería interna entre usuarios registrados — los únicos mecanismos de comunicación son `Comunicacion` (broadcast institucional) y `Aviso` (notificaciones del sistema).

Este change agrega la capa faltante: edición de perfil propio (sin admin) y mensajería interna thread-based.

## Goals / Non-Goals

**Goals:**

- Endpoint `GET /api/perfil` que devuelve la info del usuario autenticado (con PII desencriptada)
- Endpoint `PUT /api/perfil` que permite editar campos editables del propio perfil
- CUIL como solo lectura desde perfil (no modificable por el usuario)
- Modelo `Mensaje` con patrón thread: un mensaje raíz crea un hilo, las respuestas se vinculan por `thread_id`
- Endpoint `GET /api/inbox` que lista hilos activos del usuario autenticado (con paginación)
- Endpoint `GET /api/inbox/{id}` que devuelve un hilo completo con todos sus mensajes
- Endpoint `POST /api/inbox/{id}/responder` que agrega una respuesta al hilo
- Nuevos permisos: `perfil:editar`, `inbox:leer`, `inbox:responder`
- Asignación de permisos en seed de migración para TUTOR, PROFESOR, COORDINADOR, ADMIN
- Verificar que `POST /api/auth/logout` funciona como cierre de sesión explícito (sin cambios)
- Nueva migración Alembic (`016_mensajes_permisos.py`)

**Non-Goals:**

- Envío de mensajes nuevos (crear un nuevo hilo desde cero) — solo recepción y respuesta dentro de hilos existentes
- Notificaciones push, emails, WebSockets
- Adjuntos en mensajes
- Edición o eliminación de mensajes enviados
- Bandeja de salida o mensajes enviados (solo inbox/recepción)
- Panel admin de mensajes global

## Decisions

### D1 — Modelo `Mensaje`: single-table con thread_id auto-referencial

Se usa una sola tabla `mensajes` donde el primer mensaje de un hilo tiene `thread_id = NULL` y las respuestas apuntan al `id` de ese mensaje raíz vía `thread_id`. Esto evita una tabla separada `Thread` y simplifica las queries: un `SELECT ... WHERE thread_id = :raiz_id` obtiene todo el hilo ordenado por fecha.

**Alternativa descartada**: tabla `Thread` separada con relación one-to-many a `Mensaje`. Se descarta porque agrega complejidad sin beneficio: siempre se necesita el mensaje raíz para mostrar asunto, y la query de hilos activos requiere aggregate sobre mensajes de todas formas.

```python
class Mensaje(Base, EntityMeta):
    __tablename__ = "mensajes"

    thread_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mensajes.id"), nullable=True, index=True
    )
    remitente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    destinatario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    asunto: Mapped[str] = mapped_column(String(200), nullable=False)
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    leido: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

Campos heredados de `EntityMeta`: `id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at` (soft delete).

### D2 — Enrutamiento: routers separados /api/perfil y /api/inbox

Se crean dos routers independientes para mantener separación de concerns:

- **`/api/perfil`**: guard `require_permission("perfil:editar")`. Siempre opera sobre `current_user`.
  - `GET /api/perfil` → `PerfilService.obtener(db, current_user)`
  - `PUT /api/perfil` → `PerfilService.actualizar(db, current_user, data)`
- **`/api/inbox`**: guards `require_permission("inbox:leer")` y `require_permission("inbox:responder")`. Siempre opera sobre `current_user` como destinatario.
  - `GET /api/inbox` → `InboxService.listar_hilos(db, current_user, pagina, page_size)`
  - `GET /api/inbox/{id}` → `InboxService.obtener_hilo(db, current_user, hilo_id)`
  - `POST /api/inbox/{id}/responder` → `InboxService.responder(db, current_user, hilo_id, cuerpo)`

### D3 — PerfilService: herencia parcial de UsuarioService

`PerfilService` reutiliza la lógica de descifrado PII de `UsuarioService._decrypt_pii()` pero NO expone los métodos admin (crear, listar todos, soft-delete). Opera exclusivamente sobre el `current_user`. Esto mantiene el principio de mínimo privilegio en la capa de servicio.

La actualización de perfil: recibe un schema `PerfilUpdate` con solo los campos editables, hace PATCH parcial (solo campos enviados), encripta PII antes de guardar, y descifra en la respuesta.

### D4 — InboxService: repositorio dedicado

`MensajeRepository` extiende `BaseRepository[Mensaje]` con métodos específicos:
- `listar_hilos(db, usuario_id, pagina, page_size)`: busca mensajes donde `destinatario_id = usuario_id AND thread_id IS NULL` (mensajes raíz), más recientes primero
- `obtener_hilo(db, hilo_id)`: busca el mensaje raíz + todas las respuestas con ese `thread_id`
- `responder(db, remitente_id, destinatario_id, thread_id, asunto, cuerpo)`: crea un nuevo mensaje con `thread_id` apuntando al raíz y swap de remitente/destinatario

El swap de remitente/destinatario en respuestas: quien responde es el remitente original como destinatario y viceversa, manteniendo la simetría del hilo.

### D5 — Permisos nuevos y seed

Siguiendo el patrón de migraciones existentes (012_avisos.py, 013_tareas.py):

```
PERMISO_CODES = ["perfil:editar", "inbox:leer", "inbox:responder"]
```

Asignación por rol (en migración, vía inserción en `rol_permisos`):
- `perfil:editar`: TUTOR, PROFESOR, COORDINADOR, ADMIN (todo usuario autenticado con perfil)
- `inbox:leer`: TUTOR, PROFESOR, COORDINADOR, ADMIN
- `inbox:responder`: TUTOR, PROFESOR, COORDINADOR, ADMIN

ALUMNO no entra en inbox (scope F3.4/F11.2 explícito: TUTOR, PROFESOR, COORDINADOR, ADMIN).

Se agregan las descripciones a `app/core/seed.py` también para referencia del seeder.

### D6 — CUIL solo lectura en perfil

`PerfilUpdate` schema NO incluye campo `cuil`. El endpoint `PUT /api/perfil` solo acepta campos editables. Si se intenta enviar `cuil`, Pydantic lo rechaza por schema (422). Esto es una restricción a nivel de API, no de modelo.

## Risks / Trade-offs

- **[Riesgo] PII en respuestas de perfil**: GET /api/perfil devuelve datos encriptados desencriptados. **Mitigación**: el endpoint requiere autenticación + permiso `perfil:editar`, y devuelve datos del propio usuario autenticado. No expone datos de terceros.
- **[Riesgo] Thread model sin tabla separada**: las queries de "todos los hilos activos del usuario" requieren filtrar por `thread_id IS NULL AND destinatario_id = :uid`. **Mitigación**: índice compuesto en `(destinatario_id, thread_id)` para la query de listado, e índice en `thread_id` para la query de detalle de hilo.
- **[Riesgo] Confusión entre mensajería interna y Comunicacion/Aviso**: los mensajes internos son 1-a-1 entre usuarios registrados, distinto de `Comunicacion` (broadcast institucional) o `Aviso` (notificación del sistema). **Mitigación**: rutas bajo `/api/inbox` claramente diferenciadas de `/api/comunicaciones` y `/api/avisos`.
