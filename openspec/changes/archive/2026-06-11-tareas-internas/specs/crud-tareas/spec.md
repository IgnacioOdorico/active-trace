## ADDED Requirements

### Requirement: CRUD de tareas
El sistema SHALL exponer endpoints para crear, editar y eliminar tareas, protegidos por el permiso `tareas:gestionar`.

#### Scenario: Crear tarea
- **WHEN** un usuario con permiso crea una tarea con asignado_a, descripción y materia_id opcional
- **THEN** el sistema crea la tarea con estado "Pendiente"
- **THEN** el sistema registra audit log

#### Scenario: Editar tarea (re-asignar)
- **WHEN** un usuario edita una tarea cambiando asignado_a
- **THEN** el sistema persiste el cambio
- **THEN** el sistema registra audit log con detalle del cambio

#### Scenario: Editar tarea inexistente
- **WHEN** un usuario intenta editar una tarea con ID inexistente
- **THEN** el sistema retorna 404

#### Scenario: Eliminar tarea (soft delete)
- **WHEN** un usuario elimina una tarea
- **THEN** el sistema marca deleted_at (soft delete)
