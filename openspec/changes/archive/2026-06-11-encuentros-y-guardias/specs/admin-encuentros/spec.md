## ADDED Requirements

### Requirement: Listado paginado de encuentros con filtros
El sistema SHALL exponer un endpoint de listado paginado de todas las `InstanciaEncuentro` del tenant, con filtros por materia, fecha y estado. El acceso es global (COORDINADOR/ADMIN ve todas las instancias del tenant).

#### Scenario: Listar encuentros sin filtros
- **WHEN** un usuario accede al listado de encuentros sin filtros
- **THEN** el sistema retorna una página con instancias del tenant ordenadas por fecha descendente
- **THEN** la respuesta incluye meta con total, página y page_size

#### Scenario: Filtrar por materia
- **WHEN** un usuario filtra encuentros por materia_id
- **THEN** el sistema retorna solo las instancias de esa materia

#### Scenario: Filtrar por rango de fechas
- **WHEN** un usuario filtra encuentros con fecha_desde y fecha_hasta
- **THEN** el sistema retorna solo las instancias dentro del rango

#### Scenario: Filtrar por estado
- **WHEN** un usuario filtra encuentros por estado "Cancelado"
- **THEN** el sistema retorna solo las instancias canceladas

#### Scenario: Paginación con límite máximo
- **WHEN** un usuario solicita page_size=200
- **THEN** el sistema limita a page_size=100
