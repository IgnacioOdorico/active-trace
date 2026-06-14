## ADDED Requirements

### Requirement: El sistema SHALL mostrar los equipos del usuario autenticado
El endpoint `GET /api/equipos/mis-equipos` DEBE devolver las asignaciones del usuario autenticado con filtros por estado, materia, rol, carrera, cohorte.

#### Scenario: Docente ve sus equipos
- **WHEN** un PROFESOR autenticado envía GET /api/equipos/mis-equipos
- **THEN** el sistema retorna 200 con todas sus asignaciones vigentes

#### Scenario: Filtrar por materia
- **WHEN** se envía GET /api/equipos/mis-equipos?materia_id={id}
- **THEN** el sistema retorna solo las asignaciones de esa materia

### Requirement: El sistema SHALL permitir asignación masiva de docentes
El endpoint `POST /api/equipos/asignacion-masiva` DEBE aceptar una lista de usuario_ids, un rol, materia_id, carrera_id, cohorte_id, comisiones, desde y hasta. Debe crear todas las asignaciones en una transacción.

#### Scenario: Asignación masiva exitosa
- **WHEN** se envía POST /api/equipos/asignacion-masiva con 3 docentes, rol=PROFESOR, materia_id=X, cohorte_id=Y
- **THEN** el sistema crea 3 asignaciones y retorna 201 con los IDs creados

#### Scenario: Asignación masiva sin permiso retorna 403
- **WHEN** se envía POST /api/equipos/asignacion-masiva sin permiso `equipos:asignar`
- **THEN** el sistema retorna 403

#### Scenario: Asignación masiva con docente inexistente falla toda la transacción
- **WHEN** se envía POST /api/equipos/asignacion-masiva con un usuario_id inválido
- **THEN** el sistema retorna 422 y no crea ninguna asignación

### Requirement: El sistema SHALL permitir clonar equipos entre períodos (RN-12)
El endpoint `POST /api/equipos/clonar` DEBE duplicar todas las asignaciones vigentes de un origen (materia × carrera × cohorte) hacia un destino con nuevas fechas `desde`/`hasta`.

#### Scenario: Clonado exitoso entre cohortes
- **WHEN** se envía POST /api/equipos/clonar con origen materia=X, cohorte_origen=A, cohorte_destino=B, desde=fecha1, hasta=fecha2
- **THEN** el sistema duplica todas las asignaciones vigentes de A a B con las nuevas fechas
- **AND** retorna 201 con las nuevas asignaciones creadas

#### Scenario: Clonado sin asignaciones origen retorna 200 con lista vacía
- **WHEN** la cohorte origen no tiene asignaciones vigentes
- **THEN** el sistema retorna 200 con una lista vacía (no es error)

### Requirement: El sistema SHALL permitir modificar vigencia general del equipo
El endpoint `PATCH /api/equipos/{id}/vigencia` DEBE actualizar `desde`/`hasta` de una asignación específica.
El endpoint `PATCH /api/equipos/vigencia-masiva` DEBE actualizar la vigencia de todas las asignaciones de un equipo (materia × cohorte).

#### Scenario: Modificar vigencia de una asignación
- **WHEN** se envía PATCH /api/equipos/{id}/vigencia con {hasta: nueva-fecha}
- **THEN** el sistema actualiza la asignación y retorna 200

#### Scenario: Modificar vigencia masiva del equipo
- **WHEN** se envía PATCH /api/equipos/vigencia-masiva con materia_id=X, cohorte_id=Y, desde=nueva-fecha, hasta=nueva-fecha
- **THEN** el sistema actualiza todas las asignaciones de ese equipo

### Requirement: El sistema SHALL exportar equipo docente a archivo
El endpoint `GET /api/equipos/{id}/exportar` DEBE generar un archivo descargable (.xlsx) con el detalle de las asignaciones del equipo.

#### Scenario: Exportar equipo exitoso
- **WHEN** se envía GET /api/equipos/{id}/exportar
- **THEN** el sistema retorna un archivo .xlsx con Content-Disposition: attachment

### Requirement: Las operaciones de escritura SHALL generar audit ASIGNACION_MODIFICAR
Toda creación, modificación o clonado de asignaciones DEBE registrar un audit log con código `ASIGNACION_MODIFICAR`.

#### Scenario: Asignación masiva genera audit
- **WHEN** se ejecuta una asignación masiva exitosa
- **THEN** el sistema registra un audit con accion="ASIGNACION_MODIFICAR" y filas_afectadas=3
