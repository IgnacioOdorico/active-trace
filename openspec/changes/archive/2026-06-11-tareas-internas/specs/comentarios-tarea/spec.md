## ADDED Requirements

### Requirement: Comentarios en tareas
El sistema SHALL permitir agregar y listar comentarios en una tarea, formando un hilo cronológico.

#### Scenario: Agregar comentario
- **WHEN** un usuario autorizado agrega un comentario a una tarea
- **THEN** el sistema persiste el comentario
- **THEN** el sistema registra audit log con accion="TAREA_COMENTAR"

#### Scenario: Listar comentarios de una tarea
- **WHEN** un usuario consulta los comentarios de una tarea
- **THEN** el sistema retorna los comentarios ordenados por creado_at ascendente

#### Scenario: Comentar en tarea sin permiso
- **WHEN** un usuario sin relación con la tarea intenta comentar
- **THEN** el sistema retorna 403

#### Scenario: Transición de estado con comentario
- **WHEN** un usuario cambia el estado de una tarea y agrega un comentario
- **THEN** el sistema persiste ambos cambios atómicamente
