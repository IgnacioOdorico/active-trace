## ADDED Requirements

### Requirement: Registro de auditoría para tareas
El sistema SHALL registrar en el audit log las acciones de creación, edición y comentarios de tareas con los códigos `TAREA_CREAR`, `TAREA_EDITAR` y `TAREA_COMENTAR` respectivamente.

#### Scenario: Auditoría al crear tarea
- **WHEN** un usuario crea una tarea
- **THEN** el sistema registra audit log con accion="TAREA_CREAR"
- **THEN** el detalle incluye tarea_id, asignado_a y asignado_por

#### Scenario: Auditoría al editar tarea
- **WHEN** un usuario edita el estado o asignado_a de una tarea
- **THEN** el sistema registra audit log con accion="TAREA_EDITAR"
- **THEN** el detalle incluye tarea_id y campos modificados

#### Scenario: Auditoría al comentar
- **WHEN** un usuario agrega un comentario a una tarea
- **THEN** el sistema registra audit log con accion="TAREA_COMENTAR"
- **THEN** el detalle incluye tarea_id y comentario_id
