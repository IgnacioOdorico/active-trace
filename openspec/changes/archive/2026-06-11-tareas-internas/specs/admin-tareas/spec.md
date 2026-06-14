## ADDED Requirements

### Requirement: Administración global de tareas
El sistema SHALL exponer un endpoint GET /api/tareas para COORDINADOR/ADMIN con listado global y filtros.

#### Scenario: Listar todas las tareas del tenant
- **WHEN** un COORDINADOR consulta todas las tareas
- **THEN** el sistema retorna tareas paginadas del tenant

#### Scenario: Filtrar por docente asignado
- **WHEN** un COORDINADOR filtra tareas por asignado_a
- **THEN** el sistema retorna solo las tareas de ese docente

#### Scenario: Filtrar por materia
- **WHEN** un COORDINADOR filtra tareas por materia_id
- **THEN** el sistema retorna solo las tareas de esa materia

#### Scenario: Filtrar por estado
- **WHEN** un COORDINADOR filtra tareas por estado "En progreso"
- **THEN** el sistema retorna solo las tareas en ese estado

#### Scenario: Búsqueda libre por descripción
- **WHEN** un COORDINADOR busca tareas por texto libre
- **THEN** el sistema retorna tareas cuya descripción contiene el texto (ILIKE)
