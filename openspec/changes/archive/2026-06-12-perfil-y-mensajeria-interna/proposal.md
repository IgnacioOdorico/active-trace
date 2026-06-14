## Why

El backend ya soporta autenticación, RBAC, y casi toda la lógica de negocio del core académico/administrativo (C-01 a C-19). Sin embargo, los usuarios autenticados no pueden editar su propio perfil ni disponen de una bandeja de mensajería interna entre usuarios registrados. Este change cierra esas brechas de experiencia de usuario y completitud del backend.

## What Changes

- **Perfil propio (F11.1)**: Nuevo endpoint `GET /api/perfil` para que el usuario autenticado vea su propia información, y `PUT /api/perfil` para editar campos editables (nombre, identificación fiscal, sexo, datos bancarios, regional, email, modalidad de cobro, matrícula profesional). CUIL se mantiene como solo lectura. Reutiliza el modelo `User` existente — no hay nuevos modelos.
- **Bandeja de mensajes interna (F3.4, F11.2, FL-10)**: Nuevo modelo `Mensaje` (thread-based) que permite a usuarios con roles TUTOR, PROFESOR, COORDINADOR, ADMIN recibir notificaciones del sistema, leer hilos de mensajes y responder dentro de un hilo. Endpoints: `GET /api/inbox` (lista hilos), `GET /api/inbox/{id}` (ver hilo), `POST /api/inbox/{id}/responder` (responder).
- **Cierre de sesión (F11.3)**: Verificar que el endpoint existente `POST /api/auth/logout` de C-03 funciona correctamente y está documentado en la capa de perfil.
- **Nuevos permisos a seed**: `perfil:editar`, `inbox:leer`, `inbox:responder`.
- **Nueva migración Alembic**: tabla `mensajes` + seed de nuevos permisos.

No hay cambios BREAKING: todos los endpoints son nuevos y los modelos existentes no se modifican estructuralmente.

## Capabilities

### New Capabilities

- `perfil-editar`: Endpoints para que el usuario autenticado vea (`GET /api/perfil`) y edite (`PUT /api/perfil`) su propio perfil. Reutiliza el modelo `User` existente. CUIL es solo lectura. Gobierna el permiso `perfil:editar`.
- `inbox-mensajeria`: Modelo `Mensaje` (thread-based), endpoints de bandeja de entrada (`GET /api/inbox`, `GET /api/inbox/{id}`, `POST /api/inbox/{id}/responder`) y seed de permisos `inbox:leer`, `inbox:responder`. Gobierna el envío/recepción de mensajes internos entre usuarios registrados del sistema.
- `cierre-sesion`: Verify que `POST /api/auth/logout` (existente de C-03) funciona correctamente como cierre de sesión explícito. Sin cambios de implementación — solo verificación.

### Modified Capabilities

<!-- Ninguna: no se modifican requisitos de specs existentes. -->

## Impact

- **Nuevo modelo**: `Mensaje` (thread-based: thread_id, remitente_id, destinatario_id, asunto, cuerpo, leido, thread padre)
- **Nuevos archivos**:
  - `backend/app/models/mensaje.py`
  - `backend/app/repositories/mensaje_repository.py`
  - `backend/app/schemas/mensaje.py`
  - `backend/app/schemas/perfil.py`
  - `backend/app/services/perfil_service.py`
  - `backend/app/services/inbox_service.py`
  - `backend/app/api/v1/routers/perfil.py`
  - `backend/app/api/v1/routers/inbox.py`
  - `backend/alembic/versions/016_mensajes_permisos.py`
- **Modificaciones**: seed de permisos en migración, registro de nuevos routers en `app/main.py`
- **Nuevos permisos**: `perfil:editar`, `inbox:leer`, `inbox:responder`
- **Habilita** la funcionalidad de perfil visible/editable y mensajería interna del frontend.
