## Context

C-07 (`usuarios-y-asignaciones`) estableció el modelo de asignaciones docentes con roles (PROFESOR, TUTOR, COORDINADOR, etc.) y contexto académico (materia, carrera, cohorte, comisiones). Sobre esa base, este change implementa Épica 6: los docentes necesitan planificar encuentros sincrónicos (F6.1–F6.2), registrarlos (F6.3), publicar el cronograma en el LMS (F6.4), y que coordinación pueda supervisar (F6.5). En paralelo, los tutores registran guardias de atención (F6.6).

El proyecto ya cuenta con:
- `EntityMeta` mixin en `backend/app/models/base.py` con `id` UUID, `tenant_id` FK, `created_at`, `updated_at`, `deleted_at`.
- `BaseRepository` en `backend/app/repositories/base.py` con filtro `tenant_id` automático, soft delete, paginación.
- `AuditLogService` en `backend/app/services/audit_service.py` con constantes de acción.
- Patrón Clean Architecture consolidado: Models → Repositories → Services → Routers.
- Guard `require_permission("modulo:accion")` en `app/core/permissions.py`.

## Goals / Non-Goals

**Goals:**
- Modelos ORM `SlotEncuentro`, `InstanciaEncuentro`, `Guardia` con `EntityMeta` y SQLAlchemy 2.0 async.
- Generación automática de N instancias al crear un slot recurrente (F6.1, RN-13).
- Creación de encuentro único sin slot padre (F6.2).
- Edición individual de instancia: estado, `meet_url`, `video_url`, `comentario` (F6.3).
- Endpoint que genera fragmento HTML listo para embeber en LMS (F6.4).
- Vista admin paginada con filtros materia, fecha, estado (F6.5).
- CRUD de guardias: tutor registra, coordinación consulta global + export (F6.6).
- Endpoints REST `/api/encuentros/*` y `/api/guardias/*` con guard `encuentros:gestionar`.
- Audit log con códigos `ENCUENTRO_CREAR`, `ENCUENTRO_EDITAR`, `GUARDIA_CREAR`.
- Tests de generación de instancias, edición, guardias.

**Non-Goals:**
- No se implementa frontend de encuentros ni guardias.
- No se integra con proveedor de videoconferencia (el docente provee el `meet_url` manualmente).
- No se implementa notificación automática a alumnos al crear/modificar encuentros.
- No se implementa calendario visual (iCalendar, Google Calendar sync).
- No se implementa edición masiva de instancias.

## Decisions

### D1: Generación de instancias en servicio (no en BD)
- **Decisión**: Al crear un `SlotEncuentro` con `cant_semanas > 0`, el servicio `EncuentroService.generar_instancias()` calcula las N fechas en Python y crea las `InstanciaEncuentro` en una transacción.
- **Alternativa considerada**: Generación vía función PostgreSQL (`generate_series`) o trigger.
- **Razón**: La lógica de negocio (calcular fechas a partir de `fecha_inicio`, `dia_semana`, `hora`, `cant_semanas`) pertenece al servicio, no a la BD. Facilita testear y mantener. La transacción garantiza atomicidad: si falla una instancia, no se persiste nada.

### D2: SlotEncuentro con dos modos: recurrente vs. fecha única
- **Decisión**: `SlotEncuentro` tiene `cant_semanas` (entero, 0 = no recurrente) y `fecha_unica` (nullable). Si `cant_semanas > 0` → genera instancias semanales desde `fecha_inicio`. Si `fecha_unica` no es nula → genera una sola instancia en esa fecha. Ambos modos son excluyentes.
- **Alternativa considerada**: Separar en dos modelos (`SlotRecurrente` y `SlotUnico`).
- **Razón**: Comparten la mayoría de los atributos (título, hora, meet_url, materia). Un solo modelo con ambos modos evita duplicación de código y simplifica la API. La validación de exclusividad se hace en el servicio.

### D3: InstanciaEncuentro desacoplada del slot después de la creación
- **Decisión**: Una vez generadas, las `InstanciaEncuentro` viven independientemente de su `SlotEncuentro`. Editar una instancia no afecta al slot ni a otras instancias. El `slot_id` es solo una referencia para trazabilidad.
- **Alternativa considerada**: Propagación de cambios del slot a todas sus instancias.
- **Razón**: Cada instancia representa un encuentro real que puede tener particularidades (se cancela, se cambia el link, se agrega comentario). Propagar cambios automáticamente del slot a instancias ya creadas podría sobrescribir datos del profesor. El slot es plantilla; las instancias son hechos consumados.

### D4: Estado de InstanciaEncuentro como String(20) con enum Python
- **Decisión**: `estado` se almacena como `String(20)` en DB con enum Python `EstadoEncuentro` (PROGRAMADO, REALIZADO, CANCELADO).
- **Alternativa considerada**: Enum nativo PostgreSQL.
- **Razón**: Consistencia con el resto del modelo (Comunicacion.estado, User.estado). Los enum Python con validación en Service son suficientes para 3 estados simples.

### D5: Fragmento HTML generado con string.Template
- **Decisión**: El endpoint de generación HTML usa `string.Template` con una plantilla HTML embebida en el servicio.
- **Alternativa considerada**: Jinja2, renderizado frontend.
- **Razón**: Es un fragmento HTML pequeño (tabla de encuentros). `string.Template` evita dependencia externa y es seguro. El HTML se genera server-side porque el consumo es por API (el profesor copia y pega en el LMS).

### D6: Guardia con modelo plano (sin recurrencia)
- **Decisión**: Cada `Guardia` es un registro independiente con fecha, horario, materia, asignación. No hay slots de guardia ni recurrencia.
- **Alternativa considerada**: Slot de guardia recurrente (similar a encuentros).
- **Razón**: Las guardias se registran después de realizadas o se planifican una por vez. No hay requerimiento de recurrencia semanal. Un modelo simple es suficiente para trazabilidad.

### D7: Un solo permiso `encuentros:gestionar` para todo el módulo
- **Decisión**: Un permiso único `encuentros:gestionar` protege todos los endpoints de encuentros y guardias.
- **Alternativa considerada**: Permisos separados (`encuentros:crear`, `encuentros:editar`, `guardias:registrar`).
- **Razón**: El módulo es relativamente pequeño y gobernado por roles (PROFESOR puede gestionar sus encuentros, COORDINADOR todos). Un permiso único sigue el principio de mínima complejidad. Si en el futuro se necesita granularidad más fina, se puede dividir sin cambios rompedores (el guard verifica existencia del permiso, no el nombre exacto).

## Risks / Trade-offs

- **[Riesgo] Generación de instancias con fecha inválida**: si `fecha_inicio` cae en día de semana distinto a `dia_semana`, calcular fechas podría dar resultados inesperados. → **Mitigación**: el servicio valida que `fecha_inicio` coincida con `dia_semana` seleccionado. Si no coincide, rechaza con DomainError.
- **[Riesgo] Volumen de instancias**: un slot con `cant_semanas = 52` genera 52 instancias. Si varios profesores crean slots largos, la tabla crece. → **Mitigación**: limite de `cant_semanas` a 52 (un año) como máximo. Filtros de paginación y soft delete mantienen la performance.
- **[Riesgo] HTML generado puede necesitar estilos específicos del LMS**: el fragmento HTML es semántico pero sin estilos. Cada LMS tiene su propia hoja de estilos. → **Mitigación**: generar HTML semántico limpio (tabla con clases CSS estándar) sin estilos inline. El profesor o el LMS aplican su propio estilo.
- **[Trade-off] Guardia sin export nativo a PDF**: el export es JSON/CSV desde la API. → **Razón**: El formato de exportación se define en la capa de presentación (frontend). La API expone datos estructurados; el frontend decide el formato de descarga.

## Migration Plan

1. Crear migración Alembic con 3 tablas: `slot_encuentro`, `instancia_encuentro`, `guardia`.
2. Crear modelos, repositorios, servicios, schemas, routers (todo código nuevo, sin cambios rompedores).
3. Crear permiso `encuentros:gestionar` en seed/catálogo de permisos.
4. Deploy: migración → código → endpoints nuevos.
5. Rollback: `DROP TABLE slot_encuentro, instancia_encuentro, guardia;` + revertir permiso seed.
