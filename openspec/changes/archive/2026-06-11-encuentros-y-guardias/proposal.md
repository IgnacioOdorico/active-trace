## Why

C-07 (`usuarios-y-asignaciones`) completó el modelo de asignaciones docentes con roles y contexto académico. Sin encuentros ni guardias, el sistema no cubre la gestión del día a día del aula: los docentes no tienen dónde registrar sus clases virtuales ni los tutores sus horas de atención. Este change implementa la Épica 6 completa (F6.1–F6.6), cerrando el ciclo planificar → ejecutar → auditar → publicar encuentros, más el registro de guardias para trazabilidad de atención tutorial.

## What Changes

- **Modelos `SlotEncuentro`, `InstanciaEncuentro`, `Guardia`**: tres nuevos modelos ORM con `EntityMeta` mixin. `SlotEncuentro` define recurrencia semanal con `cant_semanas`; `InstanciaEncuentro` representa cada ocurrencia con estado machine-driven (Programado → Realizado | Cancelado). `Guardia` registra atención tutorial con `asignacion_id`, materia, carrera, cohorte, día, horario, estado.
- **Generación de instancias recurrentes (F6.1, RN-13)**: al crear un `SlotEncuentro` con `cant_semanas > 0`, el servicio genera N `InstanciaEncuentro` a partir de `fecha_inicio` + `dia_semana` + `hora`. Cada instancia es editable individualmente.
- **Encuentro único (F6.2)**: creación directa de `InstanciaEncuentro` sin `slot_id` padre.
- **Edición de instancia (F6.3)**: PATCH sobre `InstanciaEncuentro` para modificar estado, `meet_url`, `video_url`, `comentario`.
- **Bloque HTML (F6.4)**: endpoint que renderiza un fragmento HTML con el cronograma de encuentros de una materia, listo para copiar y pegar en el LMS.
- **Vista admin encuentros (F6.5)**: listado paginado con filtros por materia, fecha, estado. Acceso global del tenant.
- **Guardias (F6.6)**: CRUD de guardias por tutor + consulta global (coordinación) + exportación.
- **Endpoints** `/api/encuentros/*` y `/api/guardias/*` con guard `encuentros:gestionar`.
- **Audit**: códigos `ENCUENTRO_CREAR`, `ENCUENTRO_EDITAR`, `GUARDIA_CREAR` en audit log.
- **Migración**: tabla `slot_encuentro`, `instancia_encuentro`, `guardia`.

## Capabilities

### New Capabilities
- `modelo-encuentros`: modelos ORM SlotEncuentro e InstanciaEncuentro con EntityMeta, estados Programado/Realizado/Cancelado, relación slot→instancia
- `encuentro-recurrente`: crear SlotEncuentro con cant_semanas y generar N instancias automáticamente (RN-13)
- `encuentro-unico`: crear InstanciaEncuentro sin slot padre
- `editar-instancia-encuentro`: editar estado, meet_url, video_url, comentario de una instancia
- `generar-html-encuentros`: endpoint que produce fragmento HTML del cronograma de encuentros
- `admin-encuentros`: listado paginado de encuentros con filtros (materia, fecha, estado), acceso global tenant
- `modelo-guardia`: modelo ORM Guardia con EntityMeta, estados Pendiente/Realizada/Cancelada
- `crud-guardias`: CRUD de guardias para tutores + consulta global coordinación + export
- `audit-encuentros`: registro de auditoría códigos `ENCUENTRO_CREAR`, `ENCUENTRO_EDITAR`, `GUARDIA_CREAR`

### Modified Capabilities
- *(ninguna — todas son nuevas)*

## Impact

- **Models**: nuevos `backend/app/models/slot_encuentro.py`, `instancia_encuentro.py`, `guardia.py` — todos con `EntityMeta` mixin.
- **Repositories**: nuevos `SlotEncuentroRepository`, `InstanciaEncuentroRepository`, `GuardiaRepository` — todos extienden `BaseRepository`.
- **Services**: nuevo `EncuentroService` con lógica de creación recurrente, edición, generación de HTML; nuevo `GuardiaService` con CRUD y export.
- **Routers**: nuevos `routers/encuentros.py` y `routers/guardias.py` bajo `/api/encuentros/*` y `/api/guardias/*`.
- **Schemas**: nuevos `schemas/encuentro.py` y `schemas/guardia.py` con modelos Pydantic.
- **Permisos**: crear permiso `encuentros:gestionar` en el catálogo de permisos.
- **Migración**: nueva migración Alembic con 3 tablas: `slot_encuentro`, `instancia_encuentro`, `guardia`.
- **Tests**: generación de instancias recurrentes, encuentro único, edición de estado, registro de guardia, export.
