## ADDED Requirements

### Requirement: Modelo ORM Tarea
El sistema SHALL tener un modelo ORM `Tarea` (tabla `tarea`) con los siguientes campos:
- `id`: UUID (PK, default uuid4)
- `tenant_id`: UUID (FK → Tenant)
- `materia_id`: UUID (FK → Materia, nullable)
- `asignado_a`: UUID (FK → Usuario)
- `asignado_por`: UUID (FK → Usuario)
- `estado`: String(20) — Pendiente | En progreso | Resuelta | Cancelada
- `descripcion`: Text
- `contexto_id`: UUID (nullable, referencia genérica)
- `created_at`, `updated_at`, `deleted_at` (desde EntityMeta)

#### Scenario: Crear tarea exitosamente
- **WHEN** un COORDINADOR crea una tarea con asignado_a, descripción y materia
- **THEN** el sistema persiste la tarea con estado "Pendiente"
- **THEN** el sistema registra asignado_por con el usuario autenticado

#### Scenario: Crear tarea sin asignado_a
- **WHEN** un usuario crea una tarea sin especificar asignado_a
- **THEN** el sistema rechaza la operación con error de validación

### Requirement: Modelo ORM ComentarioTarea
El sistema SHALL tener un modelo ORM `ComentarioTarea` (tabla `comentario_tarea`) con los siguientes campos:
- `id`: UUID (PK, default uuid4)
- `tenant_id`: UUID (FK → Tenant)
- `tarea_id`: UUID (FK → Tarea)
- `autor_id`: UUID (FK → Usuario)
- `texto`: Text
- `creado_at`: DateTime

#### Scenario: Agregar comentario a tarea
- **WHEN** un usuario agrega un comentario a una tarea existente
- **THEN** el sistema persiste el comentario con autor_id y fecha/hora actual
