## Why

Sin padrón de alumnos no se pueden importar calificaciones (C-10), ni detectar atrasados (C-11), ni comunicarse con alumnos (C-12). El padrón es la base del flujo central del PROFESOR. Además, al ser versionado, permite mantener historial de cambios sin perder datos anteriores.

## What Changes

- **Modelos `VersionPadron` y `EntradaPadron`**: versión activa por materia × cohorte, entradas con datos del alumno (nombre, email cifrado, comisión, regional).
- **Import de padrón desde `.xlsx`/`.csv`** (F1.3): subida de archivo con vista previa antes de confirmar. Usa skill `xlsx`.
- **Integración Moodle Web Services** (`integrations/moodle_ws.py`): sync de usuarios/actividades vía API del LMS. Sync nocturna + on-demand. Fallback a import manual si Moodle no responde.
- **Vaciar datos de materia** (F1.5, RN-04): endpoint para limpiar datos importados de una materia.
- **Audit `PADRON_CARGAR`** en cada importación.
- Endpoints con guards `padron:importar` (PROFESOR sobre sus materias, COORDINADOR global).
- `Migración 007: version_padron, entrada_padron`.

## Capabilities

### New Capabilities
- `gestion-padron`: importación versionada de padrón de alumnos desde archivo o Moodle WS, con vista previa, activación y limpieza.
- `integracion-moodle`: cliente Moodle Web Services con sync nocturna y on-demand, fallback a import manual.

### Modified Capabilities
- `gestion-usuarios` (de C-07): los alumnos del padrón se vinculan con usuarios existentes o se crean automáticamente al importar.

## Impact

- **Modelos**: se crea `models/version_padron.py` y `models/entrada_padron.py`.
- **Integraciones**: se crea `integrations/moodle_ws.py` como cliente Moodle WS.
- **Repositorios**: se crea `repositories/padron_repository.py`.
- **Services**: se crea `services/padron_service.py` con lógica de versionado e import.
- **Routers**: se crea `routers/padron.py` con endpoints `/api/padron/*`.
- **Schemas**: se crea `schemas/padron.py`.
- **Migración**: nueva versión Alembic `007_version_padron`.
- **Tests**: versionado (activar desactiva anterior), import xlsx/csv, entrada sin usuario_id, aislamiento tenant, mock Moodle WS + fallback 502.
- **Skill `xlsx`**: necesaria para procesar archivos .xlsx/.csv de padrón.
