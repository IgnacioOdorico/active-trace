## Why

C-07 (`usuarios-y-asignaciones`) estableció el modelo de asignaciones docentes con roles académicos. Sin evaluaciones ni coloquios, el sistema no cubre la gestión de instancias evaluativas finales: los coordinadores no tienen dónde crear convocatorias de coloquio con cupos, los alumnos no pueden reservar turno, y no existe trazabilidad de resultados académicos consolidados. Este change implementa la funcionalidad F7.1–F7.5 (Panel de métricas, Importar alumnos, Crear convocatoria, Listado de convocatorias, Admin global) más el flujo FL-07 de reserva de turno por alumno.

## What Changes

- **Modelos `Evaluacion`, `ReservaEvaluacion`, `ResultadoEvaluacion`**: tres nuevos modelos ORM con `EntityMeta` mixin. `Evaluacion` es cabecera de convocatoria con tipo (Parcial | TP | Coloquio | Recuperatorio), instancia, días disponibles. `ReservaEvaluacion` vincula alumno a evaluación con estado Activa/Cancelada. `ResultadoEvaluacion` registra nota final.
- **Crear convocatoria de coloquio (F7.3)**: endpoint que define materia, instancia, días disponibles y cupos. El sistema genera slots de tiempo reservables con control de cupo.
- **Importar alumnos a convocatoria (F7.2)**: carga/actualiza el padrón de alumnos habilitados para una evaluación.
- **Reserva de turno por alumno (FL-07)**: el alumno selecciona día disponible con cupo > 0 y reserva. La reserva decrementa el cupo. Estado Activa/Cancelada. Solo ALUMNO puede reservar.
- **Listado de convocatorias (F7.4)**: vista tabular con métricas por convocatoria (materia, instancia, días, convocados, reservas activas, cupos libres).
- **Panel de métricas (F7.1)**: total alumnos cargados, instancias activas, reservas activas, notas registradas.
- **Admin global (F7.5)**: gestión de convocatorias (alta, edición, cierre), registro académico consolidado, agenda de reservas activas.
- **Endpoints** `/api/coloquios/*` con guards `coloquios:gestionar` (COORDINADOR/ADMIN) y `coloquios:reservar` (ALUMNO).
- **Audit**: códigos `COLOQUIO_CREAR`, `COLOQUIO_RESERVAR`, `COLOQUIO_CERRAR` en audit log.
- **Migración**: tablas `evaluacion`, `reserva_evaluacion`, `resultado_evaluacion`.

## Capabilities

### New Capabilities
- `modelo-evaluacion`: modelos ORM Evaluacion, ReservaEvaluacion, ResultadoEvaluacion con EntityMeta, tipos y estados
- `convocatoria-coloquio`: crear convocatoria con días y cupos, importar alumnos habilitados
- `reserva-coloquio`: alumno reserva turno con decremento de cupo, cancelación, control de cupo agotado
- `resultado-coloquio`: registro de notas finales por evaluación y alumno
- `metricas-coloquio`: panel con métricas de convocatoria (convocados, reservas, cupos libres)
- `admin-coloquios`: listado de convocatorias, agenda de reservas, admin global
- `audit-coloquios`: constantes COLOQUIO_CREAR, COLOQUIO_RESERVAR, COLOQUIO_CERRAR en audit log

### Modified Capabilities
- *(ninguna — todas son nuevas)*

## Impact

- **Models**: nuevos `backend/app/models/evaluacion.py`, `reserva_evaluacion.py`, `resultado_evaluacion.py` — todos con `EntityMeta` mixin.
- **Repositories**: nuevos `EvaluacionRepository`, `ReservaEvaluacionRepository`, `ResultadoEvaluacionRepository` — todos extienden `BaseRepository`.
- **Services**: nuevo `ColoquioService` con lógica de creación de convocatoria, importación de alumnos, reserva con decremento de cupo, métricas, admin global.
- **Routers**: nuevo `routers/coloquios.py` bajo `/api/coloquios/*`.
- **Schemas**: nuevo `schemas/coloquio.py` con modelos Pydantic.
- **Permisos**: crear permisos `coloquios:gestionar` y `coloquios:reservar` en el catálogo de permisos.
- **Migración**: nueva migración Alembic con 3 tablas: `evaluacion`, `reserva_evaluacion`, `resultado_evaluacion`.
- **Tests**: creación de convocatoria con cupos, reserva decrementa cupo, sin cupo rechaza, métricas, resultado consolidado.
