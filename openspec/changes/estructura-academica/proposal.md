## Why

First business domain entities after security foundation. Carrera, Cohorte, and Materia are the core academic catalog that all downstream features (usuarios, equipos, calificaciones, programas) depend on.

## What Changes

- New model `Carrera` (degree program): `codigo` unique per tenant, `nombre`, `descripcion`, `activa` (default True)
- New model `Cohorte` (cohort): `nombre` unique per (tenant, carrera), `carrera_id` FK, `fecha_inicio`, `fecha_fin`, `activa` (default True)
- New model `Materia` (subject): `codigo` unique per tenant, `nombre`, `descripcion`, `carrera_id` FK (nullable)
- ABM admin endpoints at `/api/admin/carreras`, `/api/admin/cohortes`, `/api/admin/materias` guarded with `estructura:gestionar`
- Migration 004 creating carrera, cohorte, materia tables
- Business rule: inactive carrera cannot reference active cohorts

## Capabilities

### New Capabilities
- `carrera-model`: Carrera entity with tenant-scoped CRUD and uniqueness by codigo
- `cohorte-model`: Cohorte entity with tenant+carrera scoped CRUD, tied to Carrera lifecycle
- `materia-model`: Materia entity with tenant-scoped CRUD, optional carrera FK

### Modified Capabilities

## Impact

- New models: `backend/app/models/carrera.py`, `cohorte.py`, `materia.py`
- New repositories: `backend/app/repositories/carrera.py`, `cohorte.py`, `materia.py`
- New services: `backend/app/services/estructura.py` with business rule validation
- New endpoints in admin router or new router `estructura.py` under admin prefix
- Migration 004 under `backend/alembic/versions/`
- Tests for CRUD, uniqueness, multi-tenant isolation, state transitions
