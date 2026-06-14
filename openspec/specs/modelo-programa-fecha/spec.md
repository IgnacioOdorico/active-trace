## ADDED Requirements

### Requirement: Modelo ORM ProgramaMateria
El sistema SHALL tener un modelo ORM `ProgramaMateria` (tabla `programa_materia`) con los siguientes campos:
- `id`: UUID (PK, default uuid4)
- `tenant_id`: UUID (FK → Tenant)
- `materia_id`: UUID (FK → Materia)
- `carrera_id`: UUID (FK → Carrera)
- `cohorte_id`: UUID (FK → Cohorte)
- `titulo`: String(200)
- `referencia_archivo`: String(500) — referencia opaca al archivo
- `cargado_at`: DateTime
- `created_at`, `updated_at`, `deleted_at` (desde EntityMeta)

#### Scenario: Crear programa exitosamente
- **WHEN** un COORDINADOR crea un programa con materia_id, carrera_id, cohorte_id, titulo y referencia_archivo
- **THEN** el sistema persiste el programa con cargado_at = ahora

### Requirement: Modelo ORM FechaAcademica
El sistema SHALL tener un modelo ORM `FechaAcademica` (tabla `fecha_academica`) con los siguientes campos:
- `id`: UUID (PK, default uuid4)
- `tenant_id`: UUID (FK → Tenant)
- `materia_id`: UUID (FK → Materia)
- `cohorte_id`: UUID (FK → Cohorte)
- `tipo`: String(20) — Parcial | TP | Coloquio | Recuperatorio
- `numero`: Integer — número de instancia
- `periodo`: String(20) — ej: "2026-1"
- `fecha`: Date
- `titulo`: String(200)
- `created_at`, `updated_at`, `deleted_at` (desde EntityMeta)

#### Scenario: Crear fecha académica exitosamente
- **WHEN** un COORDINADOR crea una fecha académica con materia_id, cohorte_id, tipo, numero, periodo, fecha y titulo
- **THEN** el sistema persiste la fecha académica
