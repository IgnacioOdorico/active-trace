## ADDED Requirements

### Requirement: Vista de mis equipos del docente
La feature SHALL mostrar al usuario las asignaciones donde participa (materia, rol, carrera, cohorte, comisiones, vigencia, estado), obtenidas de `GET /api/equipos/mis-equipos`, con filtros por estado de vigencia, materia y rol. La carga de datos SHALL realizarse mediante un hook de TanStack Query sobre `apiClient`, nunca con fetch directo en el componente.

#### Scenario: Listado con filtros aplicados
- **WHEN** el usuario con permiso `equipos:asignar` abre la vista y selecciona un filtro de materia
- **THEN** la feature llama `GET /api/equipos/mis-equipos?materia_id=...` y renderiza solo las asignaciones que coinciden

#### Scenario: Estado vacío
- **WHEN** el endpoint devuelve `data: []`
- **THEN** la feature muestra un estado informativo "sin equipos asignados" y no rompe la tabla

### Requirement: Asignación masiva de docentes
La feature SHALL permitir seleccionar múltiples docentes y asignarlos en bloque a una combinación materia × carrera × cohorte × rol con vigencia, enviando `POST /api/equipos/asignacion-masiva`. El formulario SHALL validarse con React Hook Form + Zod antes de enviar.

#### Scenario: Asignación masiva exitosa
- **WHEN** el usuario completa el formulario válido y confirma
- **THEN** la feature envía el request, muestra confirmación e invalida la query de equipos para refrescar el listado

#### Scenario: Error de FK / usuario inválido
- **WHEN** el backend responde 422 por usuario_id inválido o violación de FK
- **THEN** la feature muestra el mensaje de error sin perder los datos cargados en el formulario

### Requirement: Clonar equipo docente entre períodos
La feature SHALL permitir clonar las asignaciones de un equipo origen hacia un destino (nueva cohorte) mediante `POST /api/equipos/clonar`, mostrando los ids creados.

#### Scenario: Clonado con asignaciones vigentes
- **WHEN** el usuario selecciona equipo origen y cohorte destino y confirma
- **THEN** la feature muestra la cantidad de asignaciones clonadas y refresca el listado

#### Scenario: Origen sin asignaciones vigentes
- **WHEN** el backend responde 200 con `ids_creados: []`
- **THEN** la feature informa que no había asignaciones vigentes para clonar

### Requirement: Modificar vigencia individual y en bloque
La feature SHALL permitir modificar la vigencia (desde/hasta) de una asignación con `PATCH /api/equipos/{id}/vigencia` y de todo un equipo con `PATCH /api/equipos/vigencia-masiva`. El schema SHALL validar que `desde` sea anterior a `hasta`.

#### Scenario: Modificación masiva de vigencia
- **WHEN** el usuario ajusta las fechas de un equipo y confirma
- **THEN** la feature envía `vigencia-masiva` y muestra la cantidad de filas afectadas

### Requirement: Exportar equipo docente
La feature SHALL permitir descargar el detalle de un equipo mediante `GET /api/equipos/{id}/exportar`, manejando la respuesta binaria como descarga de archivo.

#### Scenario: Descarga de export
- **WHEN** el usuario hace clic en "Exportar" sobre una asignación
- **THEN** el navegador descarga el archivo generado por el backend
