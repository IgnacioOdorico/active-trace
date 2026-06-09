## Why

Sin calificaciones no hay análisis académico posible. C-09 habilitó el padrón de alumnos; ahora necesitamos importar las notas desde el LMS para poder detectar atrasados (C-11), rankear actividades (C-11) y comunicarnos con alumnos (C-12). Además, el umbral de aprobación es un prerrequisito de cualquier cómputo de "aprobado".

## What Changes

- **Modelos `Calificacion` y `UmbralMateria`**: nota numérica y/o textual por alumno-actividad, `aprobado` derivado según umbral y conjunto aprobatorio.
- **Import de calificaciones desde archivo LMS** (F1.1): subida de archivo, detección de columnas numéricas (RN-01) y textuales (RN-02), vista previa, selección de actividades a incluir.
- **Import de reporte de finalización** (F1.2): cruce contra calificaciones importadas para detectar TPs entregados sin nota.
- **Configurar umbral por materia** (F2.1, RN-03, defecto 60%): endpoint para definir el porcentaje mínimo aprobatorio y valores textuales aprobatorios. Scope aislado por asignación (no afecta otros docentes).
- **Audit `CALIFICACIONES_IMPORTAR`** en cada importación.
- Endpoints con guards `calificaciones:importar` (PROFESOR sobre sus materias, COORDINADOR global).
- `Migración 0NN: calificacion, umbral_materia`.

## Capabilities

### New Capabilities
- `gestion-calificaciones`: importación de calificaciones desde archivo LMS, detección de columnas, vista previa, selección de actividades, import de reporte de finalización.
- `gestion-umbral`: configuración del umbral de aprobación por materia (porcentaje y valores textuales aprobatorios), scope aislado por asignación.

### Modified Capabilities
<!-- No existing capabilities change their requirements. -->

## Impact

- **Modelos**: se crea `models/calificacion.py` y `models/umbral_materia.py`.
- **Repositorios**: se crea `repositories/calificacion_repository.py` y `repositories/umbral_repository.py`.
- **Services**: se crea `services/calificacion_service.py` (import, preview, activity selection, completion report) y `services/umbral_service.py` (configuración por asignación).
- **Routers**: se crea `routers/calificaciones.py` con endpoints `/api/calificaciones/*` y `routers/umbral.py` con `/api/umbral/*`.
- **Schemas**: se crea `schemas/calificacion.py` y `schemas/umbral.py`.
- **Migración**: nueva versión Alembic con tablas `calificacion` y `umbral_materia`.
- **Tests**: derivación `aprobado`, import + preview, selección de actividades, umbral por asignación (no afecta otros docentes).
