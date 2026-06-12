## Context

C-06 (`estructura-academica`) estableció los modelos Carrera, Cohorte, Materia que este change necesita como contexto de asociación. Sobre esa base, este change implementa F5.3 (programas de materia) y F5.4 (fechas académicas): dos módulos livianos de gestión documental y calendarización.

## Goals / Non-Goals

**Goals:**
- Modelos ORM `ProgramaMateria` y `FechaAcademica` con EntityMeta.
- ABM de programas: upload con referencia_archivo, asociación materia×carrera×cohorte.
- CRUD de fechas académicas: tipo, número, fecha, período, título.
- Fragmento de contenido LMS con las fechas registradas.
- Endpoints REST bajo `/api/programas` y `/api/fechas-academicas`.

**Non-Goals:**
- No se implementa almacenamiento de archivos real (referencia_archivo es un string opaco).
- No se implementa calendario visual (el frontend lo hará).
- No se validan conflictos de fechas.

## Decisions

### D1: referencia_archivo como string opaco
- **Decisión**: El campo `referencia_archivo` almacena una referencia al archivo (URL, path, key de S3, etc.). El sistema no valida que la referencia sea accesible.
- **Razón**: El almacenamiento de archivos es responsabilidad de una capa futura. El modelo solo guarda la referencia.

### D2: Un permiso existente `estructura:gestionar`
- **Decisión**: Los endpoints de programas y fechas académicas reusan el permiso `estructura:gestionar` existente (COORDINADOR, ADMIN).
- **Razón**: Son operaciones de gestión de estructura académica. No justifica permisos nuevos.

## Risks / Trade-offs

- **[Trade-off] Sin validación de conflictos**: dos evaluaciones el mismo día para la misma materia no generan warning. → **Razón**: la validación de conflictos es responsabilidad del usuario al cargar. Se puede agregar en el futuro.
