## Why

C-11 (`analisis-atrasados-reportes`) completó la detección de alumnos en riesgo. Sin el canal de comunicación, el profesor no puede cerrar el ciclo: identificar al alumno atrasado y notificarlo. Este change implementa el worker de cola asíncrono (F3.2), con preview obligatorio (F3.1), aprobación humana configurable por tenant (F3.3), y el modelo `Comunicacion` con destinatario cifrado, estados machine-driven y tracking de lotes.

## What Changes

- **Modelo `Comunicacion`**: nuevo modelo ORM con destinatario `[cifrado]` (AES-256 vía `security.py`), `lote_id` para agrupar envíos masivos, máquina de estados `Pendiente → Enviando → Enviado | Error | Cancelado`. Si tenant requiere aprobación: `Nueva → PendienteAprobacion → [aprobar] → Pendiente`.
- **Worker asíncrono** en `backend/app/workers/`: proceso Python separado que consume la cola, procesa `Pendiente → Enviando → Enviado/Error` con reintentos (< 3 → `Pendiente` backoff, ≥ 3 → `Error`). Plantillas con variables de sustitución (`{nombre}`, `{materia}`, etc.).
- **Preview obligatorio** (F3.1, RN-16): endpoint que renderiza asunto + cuerpo con variables sustituidas antes de encolar.
- **Envío masivo con cola** (F3.2): un lote agrupa N comunicaciones; el worker procesa secuencialmente.
- **Aprobación humana configurable por tenant** (F3.3, RN-17): si tenant tiene `requiere_aprobacion_comunicaciones = true`, los mensajes van a `Nueva → PendienteAprobacion`; el guard `comunicacion:aprobar` permite aprobar lote o individual. Al aprobar → `Pendiente`.
- **Endpoints** `/api/comunicaciones/*` con guard `comunicacion:enviar` y `comunicacion:aprobar`.
- **Audit**: código `COMUNICACION_ENVIAR` en audit log.
- **Migración 009**: tabla `comunicacion` y columna `tenant.requiere_aprobacion_comunicaciones`.

## Capabilities

### New Capabilities
- `modelo-comunicacion`: modelo ORM, máquina de estados con transiciones válidas, cifrado de destinatario, lote_id
- `worker-cola`: proceso worker asíncrono que consume Pendiente → Enviando → Enviado/Error con backoff y reintentos
- `preview-comunicacion`: preview de plantilla con variables de sustitución antes de encolar
- `aprobacion-comunicacion`: aprobación humana configurable por tenant, lote o individual, guard `comunicacion:aprobar`
- `endpoints-comunicacion`: CRUD de comunicaciones, envío masivo, consulta de estado, cancelación
- `audit-comunicacion`: registro de auditoría código `COMUNICACION_ENVIAR`

### Modified Capabilities
- *(ninguna — todas son nuevas)*

## Impact

- **Models**: nuevo `backend/app/models/comunicacion.py` con `Comunicacion` (Base, EntityMeta). Se añade campo `requiere_aprobacion_comunicaciones` a `Tenant`.
- **Repositories**: nuevo `ComunicacionRepository` (extiende `BaseRepository`) con métodos para batch update de estado, consulta por lote, filtros de cola (Pendientes).
- **Services**: nuevo `ComunicacionService` con lógica de preview, envío (encolar), aprobación, cancelación, consulta de estado.
- **Worker**: nuevo `backend/app/workers/comunicacion_worker.py` con lógica de procesamiento de cola. `main.py` se actualiza para disparar el worker.
- **Routers**: nuevo `routers/comunicaciones.py` con endpoints bajo `/api/comunicaciones/*`.
- **Schemas**: nuevo `schemas/comunicacion.py` con modelos Pydantic para requests/responses.
- **Core**: se reusa `app/core/security.py` (encrypt/decrypt) para destinatario `[cifrado]`.
- **Migración**: nueva migración Alembic `009` para tabla `comunicacion` y columna en `tenant`.
- **Tests**: unidad de máquina de estados (transiciones válidas/inválidas), preview, aprobación lote/individual, cancelación, cifrado/descifrado de destinatario, worker processing.
