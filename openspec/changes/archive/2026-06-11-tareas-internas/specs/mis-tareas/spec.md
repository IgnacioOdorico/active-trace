## ADDED Requirements

### Requirement: Mis tareas (vista del docente)
El sistema SHALL exponer un endpoint GET /api/tareas/mias que retorna las tareas asignadas al usuario autenticado.

#### Scenario: Listar mis tareas
- **WHEN** un PROFESOR consulta sus tareas
- **THEN** el sistema retorna las tareas donde asignado_a = usuario autenticado
- **THEN** las tareas se ordenan por created_at descendente

#### Scenario: Filtrar mis tareas por estado
- **WHEN** un PROFESOR filtra sus tareas por estado "Pendiente"
- **THEN** el sistema retorna solo las tareas en ese estado

#### Scenario: Sin tareas asignadas
- **WHEN** un usuario sin tareas consulta sus tareas
- **THEN** el sistema retorna una lista vacía
