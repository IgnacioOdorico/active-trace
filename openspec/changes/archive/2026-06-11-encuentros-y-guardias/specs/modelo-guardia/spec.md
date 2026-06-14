## ADDED Requirements

### Requirement: Modelo ORM Guardia
El sistema SHALL tener un modelo ORM `Guardia` (tabla `guardia`) con los siguientes campos:
- `id`: UUID (PK, default uuid4)
- `tenant_id`: UUID (FK → Tenant)
- `asignacion_id`: UUID (FK → Asignacion, quien cubre la guardia)
- `materia_id`: UUID (FK → Materia)
- `carrera_id`: UUID (FK → Carrera)
- `cohorte_id`: UUID (FK → Cohorte, nullable)
- `dia`: String(15) — Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo
- `horario`: String(20) — rango horario (ej: "14:00–14:45")
- `estado`: String(20) — Pendiente|Realizada|Cancelada
- `comentarios`: Text (nullable)
- `created_at`, `updated_at`, `deleted_at` (desde EntityMeta)

#### Scenario: Crear guardia exitosamente
- **WHEN** un tutor registra una guardia con asignacion_id, materia_id, dia y horario
- **THEN** el sistema persiste la guardia con estado "Pendiente"
- **THEN** el tenant_id se asigna automáticamente

#### Scenario: Guardia con datos mínimos
- **WHEN** un tutor registra una guardia solo con asignacion_id, materia_id, dia y horario
- **THEN** el sistema persiste la guardia exitosamente
- **THEN** comentarios es NULL

#### Scenario: Guardia sin asignacion_id es rechazada
- **WHEN** un usuario crea una guardia sin asignacion_id
- **THEN** el sistema rechaza la operación con error de validación

### Requirement: Transición de estado de Guardia
El sistema SHALL validar las transiciones de estado de Guardia: Pendiente → Realizada, Pendiente → Cancelada.

#### Scenario: Marcar guardia como realizada
- **WHEN** un usuario cambia el estado de Pendiente a Realizada
- **THEN** el sistema persiste el cambio

#### Scenario: Cancelar guardia
- **WHEN** un usuario cambia el estado de Pendiente a Cancelada
- **THEN** el sistema persiste el cambio

#### Scenario: Rechazar transición inválida
- **WHEN** un usuario intenta cambiar una guardia de Cancelada a Pendiente
- **THEN** el sistema rechaza la operación con DomainError
