## Why

El sistema necesita centralizar los programas oficiales de las materias y las fechas de evaluaciones (parciales, TPs, coloquios) por cohorte. Hoy estos datos se manejan fuera del sistema (archivos sueltos, calendarios informales). Este change implementa F5.3 (gestión de programas) y F5.4 (gestión de fechas académicas), cubriendo: subir y asociar el programa de cada materia×carrera×cohorte, y registrar el calendario de evaluaciones con vista tabular y generación de contenido para el LMS.

## What Changes

- Modelos `ProgramaMateria` y `FechaAcademica` con EntityMeta.
- `/api/programas`: upload + asociar programa (archivo + metadatos), listar por materia/carrera/cohorte.
- `/api/fechas-academicas`: CRUD de fechas de evaluación por materia×cohorte×número de instancia.
- Generación de fragmento de contenido listo para el LMS (F5.4).
- Migración Alembic con tablas `programa_materia` y `fecha_academica`.
- Endpoints REST con guard `estructura:gestionar` (ADMIN/COORDINADOR).

## Capabilities

### New Capabilities
- `modelo-programa-fecha`: modelos ORM ProgramaMateria y FechaAcademica con EntityMeta
- `programas-materia`: ABM de programas, upload de archivo, asociación materia×carrera×cohorte
- `fechas-academicas`: CRUD de fechas de evaluación, listado tabular, fragmento LMS

### Modified Capabilities
- *(ninguna — todas son nuevas)*

## Impact

- **Models**: nuevos `backend/app/models/programa_materia.py`, `fecha_academica.py`.
- **Repositories**: `ProgramaMateriaRepository`, `FechaAcademicaRepository`.
- **Services**: `ProgramaService`, `FechaAcademicaService`.
- **Routers**: `routers/programas.py`, `routers/fechas_academicas.py`.
- **Schemas**: `schemas/programa.py`, `schemas/fecha_academica.py`.
- **Migración**: 2 tablas: `programa_materia`, `fecha_academica`.
