## ADDED Requirements

### Requirement: Panel de métricas de coloquios
La feature SHALL mostrar al usuario con permiso de coordinación las métricas de coloquios desde `GET /api/coloquios/metricas`: total de alumnos cargados, instancias activas, reservas activas y notas registradas.

#### Scenario: Render de métricas
- **WHEN** el coordinador abre el panel de coloquios
- **THEN** la feature muestra las cuatro métricas obtenidas del endpoint

### Requirement: Crear y administrar convocatorias
La feature SHALL permitir crear una convocatoria de coloquio (`POST /api/coloquios`) definiendo materia, instancia, días y cupos; editarla (`PATCH /api/coloquios/{id}`) y cerrarla (`PATCH /api/coloquios/{id}/cerrar`). El formulario SHALL validarse con React Hook Form + Zod.

#### Scenario: Crear convocatoria
- **WHEN** el coordinador completa una convocatoria válida con días y cupos y confirma
- **THEN** la feature envía el POST, muestra confirmación e invalida el listado de convocatorias

#### Scenario: Cerrar convocatoria
- **WHEN** el coordinador cierra una convocatoria
- **THEN** la feature envía el PATCH de cierre y refleja el nuevo estado

### Requirement: Importar alumnos a una convocatoria
La feature SHALL permitir cargar o actualizar el padrón de alumnos habilitados de una convocatoria mediante `POST /api/coloquios/{id}/alumnos`.

#### Scenario: Importación de alumnos
- **WHEN** el coordinador importa el listado de alumnos habilitados
- **THEN** la feature envía el request y actualiza el contador de convocados

### Requirement: Listado de convocatorias con métricas operativas
La feature SHALL mostrar el listado de convocatorias desde `GET /api/coloquios` con materia, instancia, días disponibles, convocados, reservas activas y cupos libres, más acciones de gestión.

#### Scenario: Listado tabular
- **WHEN** el coordinador abre el listado de convocatorias
- **THEN** la feature renderiza cada convocatoria con sus métricas operativas y acciones disponibles
